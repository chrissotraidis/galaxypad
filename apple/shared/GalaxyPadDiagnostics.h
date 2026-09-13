// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from SunPad fcdc1411e483a86ca80ec82e7cd53839c51ff865,
// apple/shared/SunPadDiagnostics. Galaxy privacy and size bounds strengthened.
#pragma once

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

/* Starts the persistent runtime log and rotates it when it grows beyond 1 MB.
 * The log lives under GalaxyPad/Logs in Application Support on iOS and Caches on
 * tvOS, where filesystem-backed state must be treated as purgeable. */
FOUNDATION_EXPORT void GalaxyPadDiagnosticsStart(void);

/* Writes one timestamped line to both the unified device log and GalaxyPad's
 * persistent runtime log. Intended for low-frequency lifecycle breadcrumbs,
 * not per-frame tracing. */
FOUNDATION_EXPORT void GalaxyPadLog(NSString *format, ...) NS_FORMAT_FUNCTION(1, 2);

/* Records a warning/error emitted by the embedded runtime. Repeated identical
 * known event codes are counted and rate-limited so a failure cannot flood the
 * log. Only allowlisted constant phrases are classified; raw message arguments
 * are discarded. Unrecognized events retain only severity/category/count. */
FOUNDATION_EXPORT void GalaxyPadLogRuntimeEvent(
    NSString *severity, NSString *category, NSString *message);

FOUNDATION_EXPORT NSString *GalaxyPadDiagnosticsLogPath(void);

/* Sanitized, size-bounded title/body for a user-reviewed GitHub draft. These
 * helpers never read session logs, write files, or send network requests. */
FOUNDATION_EXPORT NSDictionary<NSString *, NSString *> *GalaxyPadDiagnosticsIssueDraft(
    NSDictionary<NSString *, NSString *> *reporterAnswers, NSString *technicalContext);
FOUNDATION_EXPORT NSURL *_Nullable GalaxyPadDiagnosticsIssueURL(
    NSDictionary<NSString *, NSString *> *draft);

/* Builds the single privacy-reviewed file used by the guided problem-report
 * flow. Reporter answers and current technical context lead the file, followed
 * by bounded runtime-event summaries and the current/previous app sessions. */
FOUNDATION_EXPORT NSURL *_Nullable GalaxyPadDiagnosticsReportURL(
    NSString *reportID,
    NSDictionary<NSString *, NSString *> *reporterAnswers,
    NSString *technicalContext,
    NSError **error);

NS_ASSUME_NONNULL_END
