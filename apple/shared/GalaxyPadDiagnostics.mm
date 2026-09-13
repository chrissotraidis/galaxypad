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
        @"(?i)(?:bearer\\s+|(?:token|password|secret|api[_-]?key)\\s*[:=]\\s*)(?:\"[^\"]*\"|'[^']*'|[^\\s]+)",
        @"(?:file://)?/[^\\r\\n<>\\\"]+",
        @"(?i)[a-z]:\\\\[^\\r\\n<>\\\"]+",
        @"(?i)(?:https?://)[^\\s<>]+",
        @"(?i)\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b",
        @"(?i)\\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\b",
        @"(?i)\\b[0-9a-f]{8}-[0-9a-f]{16}\\b",
        @"(?i)\\b[0-9a-f]{40}\\b",
        @"\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b",
        @"(?i)\\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\\b",
        @"(?i)(?<![0-9a-f:])(?=[0-9a-f:]*::)(?:[0-9a-f]{0,4}:){2,}[0-9a-f]{0,4}(?:%[a-z0-9]+)?(?![0-9a-f:])",
        @"(?i)(?<![0-9a-f:])(?:[0-9a-f]{1,4}:){7}[0-9a-f]{1,4}(?![0-9a-f:])",
        @"(?i)\\b[^\\s<>]+\\.(?:iso|wbfs|rvz|gcz|ciso|dol|wad|sav|bin)\\b"
    ]) {
        NSRegularExpression *expression = [NSRegularExpression regularExpressionWithPattern:pattern options:0 error:nil];
        redacted = [expression stringByReplacingMatchesInString:redacted options:0
            range:NSMakeRange(0, redacted.length) withTemplate:@"<redacted>"];
    }
    return redacted;
}

static NSString *GalaxyPadSingleLine(NSString *value, NSUInteger maximumLength) {
    NSString *single = [[GalaxyPadRedactedString(value) componentsSeparatedByCharactersInSet:
        NSCharacterSet.newlineCharacterSet] componentsJoinedByString:@" "];
    single = [single stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet];
    if (single.length > maximumLength)
        single = [[single substringWithRange:[single rangeOfComposedCharacterSequencesForRange:
            NSMakeRange(0, maximumLength)]] stringByAppendingString:@"…"];
    return single;
}

// Bound UTF-8 bytes, rather than UTF-16 units: even percent-encoded emoji must
// fit comfortably in a browser URL. Never split a composed character.
static NSString *GalaxyPadHardwareModel(void);

static NSString *GalaxyPadBoundedUTF8(NSString *value, NSUInteger budget) {
    if ([value lengthOfBytesUsingEncoding:NSUTF8StringEncoding] <= budget) return value;
    __block NSUInteger bytes = 0, end = 0;
    [value enumerateSubstringsInRange:NSMakeRange(0, value.length)
        options:NSStringEnumerationByComposedCharacterSequences
        usingBlock:^(NSString *substring, NSRange range, NSRange enclosing, BOOL *stop) {
            (void)enclosing;
            NSUInteger size = [substring lengthOfBytesUsingEncoding:NSUTF8StringEncoding];
            if (bytes + size + 3 > budget) { *stop = YES; return; }
            bytes += size;
            end = NSMaxRange(range);
        }];
    return [[value substringToIndex:end] stringByAppendingString:@"…"];
}

NSDictionary<NSString *, NSString *> *GalaxyPadDiagnosticsIssueDraft(
    NSDictionary<NSString *, NSString *> *reporterAnswers, NSString *technicalContext) {
    NSString *(^answer)(NSString *) = ^NSString *(NSString *key) {
        NSString *value = GalaxyPadBoundedUTF8(GalaxyPadSingleLine(reporterAnswers[key], 500), 500);
        return value.length ? value : @"Not provided";
    };
    NSString *problem = answer(@"problem");
    NSString *title = GalaxyPadBoundedUTF8([@"[Bug]: " stringByAppendingString:
        [problem isEqualToString:@"Not provided"] ? @"GalaxyPad problem" : problem], 160);
    NSBundle *bundle = NSBundle.mainBundle;
    NSString *version = GalaxyPadSingleLine([bundle objectForInfoDictionaryKey:@"CFBundleShortVersionString"] ?: @"unknown", 60);
    NSString *build = GalaxyPadSingleLine([bundle objectForInfoDictionaryKey:@"CFBundleVersion"] ?: @"unknown", 60);
    // Put build/context first so long answers cannot displace the useful snapshot.
    NSString *body = [NSString stringWithFormat:
        @"## Technical context\nGalaxyPad %@ (build %@)\nHardware: %@\nOS: %@\n%@\n\n"
         "## What went wrong?\n%@\n\n## Area and activity\n%@\n\n## Frequency\n%@\n\n"
         "## Diagnostic log / screenshot (optional)\nAttach reviewed files here manually. The app does not upload or attach files.\n",
        version, build, GalaxyPadHardwareModel(), NSProcessInfo.processInfo.operatingSystemVersionString,
        GalaxyPadBoundedUTF8(GalaxyPadSingleLine(technicalContext, 4096), 2200),
        problem, answer(@"context"), answer(@"frequency")];
    // Normal ASCII snapshots retain all counters and answers; exceptionally
    // long/non-ASCII input is shortened in the exact draft shown for review.
    NSDictionary *draft = @{@"title": title, @"body": body};
    NSUInteger budget = [body lengthOfBytesUsingEncoding:NSUTF8StringEncoding];
    while (GalaxyPadDiagnosticsIssueURL(draft) == nil && budget > 128) {
        budget -= 128;
        draft = @{@"title": title, @"body": GalaxyPadBoundedUTF8(body, budget)};
    }
    return draft;
}

NSURL *GalaxyPadDiagnosticsIssueURL(NSDictionary<NSString *, NSString *> *draft) {
    if (!draft[@"title"].length || !draft[@"body"].length) return nil;
    NSURLComponents *components = [NSURLComponents componentsWithString:
        @"https://github.com/chrissotraidis/galaxypad/issues/new"];
    components.queryItems = @[
        [NSURLQueryItem queryItemWithName:@"title" value:draft[@"title"]],
        [NSURLQueryItem queryItemWithName:@"body" value:draft[@"body"]]
    ];
    // GitHub parses query parameters as form data, where a literal '+' means
    // space. NSURLQueryItem alone leaves '+' unescaped.
    components.percentEncodedQuery = [components.percentEncodedQuery
        stringByReplacingOccurrencesOfString:@"+" withString:@"%2B"];
    NSURL *url = components.URL;
    return url.absoluteString.length <= 7500 ? url : nil;
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

static NSString *GalaxyPadKnownRuntimeEvent(NSString *category, NSString *message) {
    if ([category isEqualToString:@"core"] && [message isEqualToString:@"boot_failed"])
        return @"boot_failed";
    // Match only fixed phrases from the embedded runtime. Never retain message
    // arguments, shader sources, guest opcodes/addresses, filenames or hashes.
    // Limit scanning even if the runtime emits a very large shader/error dump.
    NSRange prefix = NSMakeRange(0, MIN(message.length, (NSUInteger)2048));
    BOOL (^contains)(NSString *) = ^BOOL(NSString *phrase) {
        return [message rangeOfString:phrase options:NSLiteralSearch range:prefix].location != NSNotFound;
    };
    if ([category isEqualToString:@"audio"]) {
        // AudioCommon/Mixer.cpp: queue-full drops and resampling guard.
        if (contains(@"Granule Queue has completely filled and audio samples are being dropped."))
            return @"audio_granule_queue_full_samples_dropped";
        if (contains(@"needed_frames would overflow m_scratch_buffer:"))
            return @"audio_resampling_scratch_buffer_overflow";
        // DMA underruns are exposed separately by the snapshot's dmaUnderruns
        // counter; the mixer currently emits no warning for those events.
    }
    if ([category isEqualToString:@"video"] || [category isEqualToString:@"host-gpu"]) {
        // VideoCommon/AsyncShaderCompiler.cpp and Spirv.cpp.
        if (contains(@"Failed to initialize shader compiler worker") ||
            contains(@"Failed to start shader compiler worker"))
            return @"shader_compiler_worker_failure";
        if (contains(@"Failed to parse shader")) return @"shader_parse_failure";
        if (contains(@"Failed to generate SPIR-V")) return @"shader_spirv_generation_failure";
        if (contains(@"Failed to compile compute pipeline")) return @"shader_compute_pipeline_compile_failure";
    }
    if ([category isEqualToString:@"powerpc"]) {
        if (contains(@"IntCPU: Unknown instruction")) return @"powerpc_unknown_instruction";
        if (contains(@"Invalid instruction")) return @"powerpc_invalid_instruction";
    }
    return @"runtime details omitted for privacy";
}

void GalaxyPadLogRuntimeEvent(NSString *severity, NSString *category, NSString *message) {
    NSString *safeSeverity = [@[@"warning", @"error"] containsObject:severity] ? severity : @"other";
    NSString *safeCategory = [@[@"runtime", @"audio", @"video", @"powerpc", @"input",
        @"command-processor", @"core", @"fifo", @"host-gpu"] containsObject:category]
        ? category : @"other";
    NSString *safeMessage = GalaxyPadKnownRuntimeEvent(safeCategory, message ?: @"");
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

static NSString *GalaxyPadReviewedSessionLog(NSString *log) {
    NSMutableArray<NSString *> *lines = [NSMutableArray array];
    for (NSString *line in [log componentsSeparatedByCharactersInSet:NSCharacterSet.newlineCharacterSet]) {
        // Development-only input probes can exist in older/current logs. They
        // are useful locally, but raw controller/pointer samples are not reports.
        if ([line containsString:@"simulator input accepted"] ||
            [line containsString:@"controller raw_buttons="]) continue;
        [lines addObject:line];
    }
    return GalaxyPadRedactedString([lines componentsJoinedByString:@"\n"]);
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
        [report appendString:GalaxyPadReviewedSessionLog(current)];
        if (![report hasSuffix:@"\n"])
            [report appendString:@"\n"];
        [report appendString:@"\n[Previous Session]\n"];
        [report appendString:GalaxyPadReviewedSessionLog(previous)];

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
