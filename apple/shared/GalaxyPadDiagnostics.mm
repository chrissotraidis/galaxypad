// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPad fcdc1411e483a86ca80ec82e7cd53839c51ff865,
// apple/shared/SunPadDiagnostics. Galaxy privacy and size bounds strengthened.
#import "GalaxyPadDiagnostics.h"

#import <TargetConditionals.h>

#import <sys/sysctl.h>

static NSUInteger const GalaxyPadMaximumUniqueRuntimeEvents = 64;

static NSMutableDictionary<NSString *, NSMutableDictionary *> *GalaxyPadRuntimeEvents(void) {
    static NSMutableDictionary<NSString *, NSMutableDictionary *> *events;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        events = [NSMutableDictionary dictionary];
    });
    return events;
}

static NSUInteger GalaxyPadDroppedRuntimeEventKinds = 0;

static NSObject *GalaxyPadDiagnosticsLock(void) {
    static NSObject *lock;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        lock = [NSObject new];
    });
    return lock;
}

static NSString *GalaxyPadDiagnosticsDirectory(void) {
    NSSearchPathDirectory directory = NSApplicationSupportDirectory;
#if TARGET_OS_TV
    // tvOS filesystem-backed state must be treated as purgeable.
    directory = NSCachesDirectory;
#endif
    NSArray<NSString *> *paths = NSSearchPathForDirectoriesInDomains(
        directory, NSUserDomainMask, YES);
    NSString *root = [paths.firstObject stringByAppendingPathComponent:@"GalaxyPad"];
    return [root stringByAppendingPathComponent:@"Logs"];
}

NSString *GalaxyPadDiagnosticsLogPath(void) {
    return [GalaxyPadDiagnosticsDirectory() stringByAppendingPathComponent:@"runtime.log"];
}

static NSString *GalaxyPadDiagnosticsPreviousLogPath(void) {
    return [GalaxyPadDiagnosticsDirectory() stringByAppendingPathComponent:@"runtime.previous.log"];
}

static NSString *GalaxyPadRedactedString(NSString *value) {
    NSString *redacted = value ?: @"";
    NSString *temporary = NSTemporaryDirectory();
    if (temporary.length > 1)
        redacted = [redacted stringByReplacingOccurrencesOfString:temporary
                                                       withString:@"<temporary>/"];
    NSString *home = NSHomeDirectory();
    if (home.length > 0)
        redacted = [redacted stringByReplacingOccurrencesOfString:home
                                                       withString:@"<app-container>"];
    // Cover host paths outside the Simulator container too. Reports must not
    // leak development usernames, filenames, or URL credentials.
    for (NSString *pattern in @[
        @"(?:file://)?/[^\\s<>\\\"]+",
        @"(?i)(?:https?://)[^\\s<>]+",
        @"(?i)(?:bearer\\s+|(?:token|password|secret|api[_-]?key)\\s*[:=]\\s*)[^\\s]+"
    ]) {
        NSRegularExpression *expression = [NSRegularExpression regularExpressionWithPattern:pattern options:0 error:nil];
        redacted = [expression stringByReplacingMatchesInString:redacted options:0
            range:NSMakeRange(0, redacted.length) withTemplate:@"<redacted>"];
    }
    return redacted;
}

static NSString *GalaxyPadSingleLine(NSString *value, NSUInteger maximumLength) {
    NSString *single = [[value ?: @"" componentsSeparatedByCharactersInSet:
        NSCharacterSet.newlineCharacterSet] componentsJoinedByString:@" "];
    single = [single stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet];
    if (single.length > maximumLength)
        single = [[single substringToIndex:maximumLength] stringByAppendingString:@"…"];
    return GalaxyPadRedactedString(single);
}

static NSString *GalaxyPadHardwareModel(void) {
    char model[128] = {};
    size_t size = sizeof(model);
    return sysctlbyname("hw.machine", model, &size, nullptr, 0) == 0 && model[0] != '\0'
        ? @(model) : @"unknown";
}

static NSString *GalaxyPadLogTimestamp(void) {
    NSISO8601DateFormatter *formatter = [NSISO8601DateFormatter new];
    formatter.formatOptions = NSISO8601DateFormatWithInternetDateTime |
        NSISO8601DateFormatWithFractionalSeconds;
    return [formatter stringFromDate:NSDate.date];
}

void GalaxyPadDiagnosticsStart(void) {
    @synchronized (GalaxyPadDiagnosticsLock()) {
        NSFileManager *fileManager = NSFileManager.defaultManager;
        NSString *directory = GalaxyPadDiagnosticsDirectory();
        [fileManager createDirectoryAtPath:directory
               withIntermediateDirectories:YES
                                attributes:nil
                                     error:nil];

        NSString *currentPath = GalaxyPadDiagnosticsLogPath();
        if ([fileManager fileExistsAtPath:currentPath]) {
            NSString *previousPath = GalaxyPadDiagnosticsPreviousLogPath();
            [fileManager removeItemAtPath:previousPath error:nil];
            [fileManager moveItemAtPath:currentPath toPath:previousPath error:nil];
        }
        [GalaxyPadRuntimeEvents() removeAllObjects];
        GalaxyPadDroppedRuntimeEventKinds = 0;
    }

    NSBundle *bundle = NSBundle.mainBundle;
    GalaxyPadLog(@"session start version=%@ build=%@ os=%@",
              [bundle objectForInfoDictionaryKey:@"CFBundleShortVersionString"] ?: @"unknown",
              [bundle objectForInfoDictionaryKey:@"CFBundleVersion"] ?: @"unknown",
              NSProcessInfo.processInfo.operatingSystemVersionString);
    GalaxyPadLog(@"diagnostic schema=2 hardware=%@ processors=%ld physicalMemoryMiB=%.1f",
              GalaxyPadHardwareModel(), (long)NSProcessInfo.processInfo.activeProcessorCount,
              NSProcessInfo.processInfo.physicalMemory / (1024.0 * 1024.0));
}

void GalaxyPadLog(NSString *format, ...) {
    va_list arguments;
    va_start(arguments, format);
    NSString *message = [[NSString alloc] initWithFormat:format arguments:arguments];
    va_end(arguments);

    message = GalaxyPadSingleLine(message, 2048);

    NSLog(@"[GalaxyPad] %@", message);

    NSString *line = [NSString stringWithFormat:@"%@ %@\n", GalaxyPadLogTimestamp(), message];
    NSData *data = [line dataUsingEncoding:NSUTF8StringEncoding];
    if (data == nil)
        return;

    @synchronized (GalaxyPadDiagnosticsLock()) {
        NSString *path = GalaxyPadDiagnosticsLogPath();
        NSFileManager *fileManager = NSFileManager.defaultManager;
        if (![fileManager fileExistsAtPath:path])
            [fileManager createFileAtPath:path contents:nil attributes:nil];
        unsigned long long bytes = [[fileManager attributesOfItemAtPath:path error:nil] fileSize];
        if (bytes + data.length > 1024 * 1024) {
            [fileManager removeItemAtPath:GalaxyPadDiagnosticsPreviousLogPath() error:nil];
            [fileManager moveItemAtPath:path toPath:GalaxyPadDiagnosticsPreviousLogPath() error:nil];
            [fileManager createFileAtPath:path contents:nil attributes:nil];
        }
        NSFileHandle *handle = [NSFileHandle fileHandleForWritingAtPath:path];
        @try {
            [handle seekToEndOfFile];
            [handle writeData:data];
        } @catch (NSException *exception) {
            (void)exception; // Diagnostics must not crash gameplay on I/O failure.
        } @finally {
            [handle closeAndReturnError:nil];
        }
    }
}

void GalaxyPadLogRuntimeEvent(NSString *severity, NSString *category, NSString *message) {
    (void)message; // Runtime strings may contain paths, filenames, guest bytes or secrets.
    NSString *safeSeverity = [@[@"warning", @"error"] containsObject:severity] ? severity : @"other";
    NSString *safeCategory = [@[@"runtime", @"audio", @"video", @"powerpc", @"input"] containsObject:category]
        ? category : @"other";
    NSString *safeMessage = @"runtime details omitted for privacy";
    NSString *signature = [NSString stringWithFormat:@"%@|%@|%@",
                           safeSeverity, safeCategory, safeMessage];
    NSUInteger count = 0;
    BOOL shouldLog = NO;
    BOOL firstDroppedKind = NO;
    @synchronized (GalaxyPadDiagnosticsLock()) {
        NSMutableDictionary *event = GalaxyPadRuntimeEvents()[signature];
        if (event == nil) {
            if (GalaxyPadRuntimeEvents().count >= GalaxyPadMaximumUniqueRuntimeEvents) {
                ++GalaxyPadDroppedRuntimeEventKinds;
                firstDroppedKind = GalaxyPadDroppedRuntimeEventKinds == 1;
            } else {
                event = [@{
                    @"severity": safeSeverity,
                    @"category": safeCategory,
                    @"message": safeMessage,
                    @"count": @0,
                } mutableCopy];
                GalaxyPadRuntimeEvents()[signature] = event;
            }
        }
        if (event != nil) {
            count = [event[@"count"] unsignedIntegerValue] + 1;
            event[@"count"] = @(count);
            shouldLog = count == 1 || count == 10 || count == 100 || count % 1000 == 0;
        }
    }
    if (shouldLog) {
        GalaxyPadLog(@"runtime event severity=%@ category=%@ count=%lu message=%@",
                  safeSeverity, safeCategory, (unsigned long)count, safeMessage);
    } else if (firstDroppedKind) {
        GalaxyPadLog(@"runtime event unique-limit=%lu additional kinds will be summarized",
                  (unsigned long)GalaxyPadMaximumUniqueRuntimeEvents);
    }
}

static NSString *GalaxyPadRuntimeEventSummaryLocked(void) {
    NSMutableString *summary = [NSMutableString string];
    NSArray<NSString *> *signatures = [[GalaxyPadRuntimeEvents() allKeys]
        sortedArrayUsingSelector:@selector(compare:)];
    if (signatures.count == 0 && GalaxyPadDroppedRuntimeEventKinds == 0)
        return @"none\n";
    for (NSString *signature in signatures) {
        NSDictionary *event = GalaxyPadRuntimeEvents()[signature];
        [summary appendFormat:@"severity=%@ category=%@ count=%@ message=%@\n",
            event[@"severity"], event[@"category"], event[@"count"], event[@"message"]];
    }
    if (GalaxyPadDroppedRuntimeEventKinds > 0) {
        [summary appendFormat:@"additionalUniqueKinds=%lu\n",
            (unsigned long)GalaxyPadDroppedRuntimeEventKinds];
    }
    return summary;
}

static NSString *GalaxyPadBoundedSessionLog(NSString *path) {
    NSFileHandle *handle = [NSFileHandle fileHandleForReadingAtPath:path];
    if (!handle) return @"unavailable\n";
    @try {
        NSData *data = [handle readDataOfLength:1024 * 1024];
        return [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding] ?: @"unavailable\n";
    } @catch (NSException *exception) {
        (void)exception;
        return @"unavailable\n";
    } @finally {
        [handle closeAndReturnError:nil];
    }
}

NSURL *GalaxyPadDiagnosticsReportURL(
    NSString *reportID,
    NSDictionary<NSString *, NSString *> *reporterAnswers,
    NSString *technicalContext,
    NSError **error) {
    @synchronized (GalaxyPadDiagnosticsLock()) {
        NSFileManager *fileManager = NSFileManager.defaultManager;
        NSString *current = GalaxyPadBoundedSessionLog(GalaxyPadDiagnosticsLogPath());
        NSString *previous = GalaxyPadBoundedSessionLog(GalaxyPadDiagnosticsPreviousLogPath());
        NSMutableString *report = [NSMutableString string];
        [report appendString:@"GalaxyPad Diagnostic Report v2\n"];
        [report appendFormat:@"reportID=%@\n", GalaxyPadSingleLine(reportID, 80)];
        [report appendFormat:@"generated=%@\n", GalaxyPadLogTimestamp()];
        [report appendString:@"Local report; review before sharing. No automatic upload.\n\n"];
        [report appendString:@"[Reporter Answers]\n"];
        for (NSString *key in @[@"problem", @"context", @"frequency"]) {
            NSString *value = GalaxyPadSingleLine(reporterAnswers[key], 1000);
            [report appendFormat:@"%@=%@\n", key, value.length > 0 ? value : @"not provided"];
        }
        [report appendString:@"\n[Technical Context]\n"];
        [report appendString:GalaxyPadSingleLine(technicalContext ?: @"unavailable", 4096)];
        if (![report hasSuffix:@"\n"])
            [report appendString:@"\n"];
        [report appendString:@"\n[Runtime Warning/Error Summary]\n"];
        [report appendString:GalaxyPadRuntimeEventSummaryLocked()];
        [report appendString:@"\n[Current Session]\n"];
        [report appendString:GalaxyPadRedactedString(current)];
        if (![report hasSuffix:@"\n"])
            [report appendString:@"\n"];
        [report appendString:@"\n[Previous Session]\n"];
        [report appendString:GalaxyPadRedactedString(previous)];

        NSString *documents = [NSSearchPathForDirectoriesInDomains(
            NSDocumentDirectory, NSUserDomainMask, YES) firstObject];
        if (documents.length == 0)
            documents = NSTemporaryDirectory();
        NSString *directory = [documents stringByAppendingPathComponent:@"Diagnostics"];
        if (![fileManager createDirectoryAtPath:directory
                    withIntermediateDirectories:YES attributes:nil error:error]) {
            return nil;
        }
        NSString *path = [directory stringByAppendingPathComponent:
                          @"Latest-GalaxyPad-Diagnostic.log"];
        if (![report writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:error])
            return nil;
        return [NSURL fileURLWithPath:path];
    }
}
