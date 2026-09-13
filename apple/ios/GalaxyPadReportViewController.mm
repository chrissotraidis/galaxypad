// SPDX-License-Identifier: GPL-3.0-or-later
// User-reviewed GitHub drafts and optional local diagnostic-log sharing.
#import "GalaxyPadReportViewController.h"
#import "../shared/GalaxyPadDiagnostics.h"

@implementation GalaxyPadReportViewController {
  NSURL *_reportURL;
  NSDictionary<NSString *, NSString *> *_answers;
  NSDictionary<NSString *, NSString *> *_draft;
  NSString *_technicalContext;
  NSString *_logText;
  UITextView *_preview;
  UISwitch *_includeLog;
  UIButton *_shareLog;
  UIButton *_openGitHub;
}
- (instancetype)initWithReportURL:(NSURL *)url {
  if ((self = [super init])) _reportURL = url;
  return self;
}
- (instancetype)initWithReporterAnswers:(NSDictionary<NSString *, NSString *> *)answers
                      technicalContext:(NSString *)context {
  if ((self = [super init])) {
    _answers = [answers copy];
    _technicalContext = [context copy];
    _draft = GalaxyPadDiagnosticsIssueDraft(_answers, _technicalContext);
  }
  return self;
}
- (UILabel *)labelWithText:(NSString *)text {
  UILabel *label = [UILabel new];
  label.text = text;
  label.numberOfLines = 0;
  label.font = [UIFont preferredFontForTextStyle:UIFontTextStyleFootnote];
  label.adjustsFontForContentSizeCategory = YES;
  return label;
}
- (UIButton *)buttonWithTitle:(NSString *)title action:(SEL)action {
  UIButton *button = [UIButton buttonWithType:UIButtonTypeSystem];
  [button setTitle:title forState:UIControlStateNormal];
  button.titleLabel.font = [UIFont preferredFontForTextStyle:UIFontTextStyleHeadline];
  button.titleLabel.adjustsFontForContentSizeCategory = YES;
  button.titleLabel.numberOfLines = 0;
  [button addTarget:self action:action forControlEvents:UIControlEventTouchUpInside];
  [button.heightAnchor constraintGreaterThanOrEqualToConstant:44].active = YES;
  return button;
}
- (void)viewDidLoad {
  [super viewDidLoad];
  self.title = _draft ? @"Review GitHub Report" : @"Review Diagnostic Log";
  self.view.backgroundColor = UIColor.systemBackgroundColor;
  self.navigationItem.leftBarButtonItem = [[UIBarButtonItem alloc]
    initWithBarButtonSystemItem:UIBarButtonSystemItemDone target:self action:@selector(close)];
  self.navigationItem.leftBarButtonItem.accessibilityLabel = @"Close diagnostic report";
  self.navigationItem.leftBarButtonItem.accessibilityIdentifier = @"galaxypad.report.close";

  UIStackView *stack = [UIStackView new];
  stack.axis = UILayoutConstraintAxisVertical;
  stack.spacing = 12;
  stack.translatesAutoresizingMaskIntoConstraints = NO;
  UIScrollView *scroll = [UIScrollView new];
  scroll.translatesAutoresizingMaskIntoConstraints = NO;
  [self.view addSubview:scroll];
  [scroll addSubview:stack];
  UILayoutGuide *safe = self.view.safeAreaLayoutGuide;
  [NSLayoutConstraint activateConstraints:@[
    [scroll.leadingAnchor constraintEqualToAnchor:safe.leadingAnchor],
    [scroll.trailingAnchor constraintEqualToAnchor:safe.trailingAnchor],
    [scroll.topAnchor constraintEqualToAnchor:safe.topAnchor],
    [scroll.bottomAnchor constraintEqualToAnchor:safe.bottomAnchor],
    [stack.leadingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.leadingAnchor constant:16],
    [stack.trailingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.trailingAnchor constant:-16],
    [stack.topAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.topAnchor constant:12],
    [stack.bottomAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.bottomAnchor constant:-12],
    [stack.widthAnchor constraintEqualToAnchor:scroll.frameLayoutGuide.widthAnchor constant:-32]
  ]];
  if (_draft) {
    [stack addArrangedSubview:[self labelWithText:
      @"Review the draft below. Open GitHub to edit and submit it yourself; a GitHub account is required. Issues and attachments are public. Remove anything private before posting."]];
  }
  _preview = [UITextView new];
  _preview.editable = NO;
  _preview.font = [UIFont preferredFontForTextStyle:UIFontTextStyleBody];
  _preview.adjustsFontForContentSizeCategory = YES;
  _preview.accessibilityIdentifier = @"galaxypad.report.preview";
  [_preview.heightAnchor constraintEqualToConstant:300].active = YES;
  [stack addArrangedSubview:_preview];

  if (_draft) {
    _includeLog = [UISwitch new];
    _includeLog.accessibilityLabel = @"Prepare optional diagnostic log";
    _includeLog.accessibilityIdentifier = @"galaxypad.report.include-log";
    [_includeLog addTarget:self action:@selector(logChoiceChanged) forControlEvents:UIControlEventValueChanged];
    UIStackView *choice = [[UIStackView alloc] initWithArrangedSubviews:@[
      [self labelWithText:@"Prepare optional diagnostic log"], _includeLog]];
    choice.axis = UILayoutConstraintAxisHorizontal;
    choice.alignment = UIStackViewAlignmentCenter;
    choice.spacing = 12;
    [stack addArrangedSubview:choice];
    [stack addArrangedSubview:[self labelWithText:
      @"Off by default. The log adds recent app events and audio/performance context, with paths and common secrets removed. Review it, then use Share Log → Save to Files and attach it on GitHub. The browser cannot attach it automatically. Game files, saves, screenshots and raw inputs are not included in the report."]];
    _shareLog = [self buttonWithTitle:@"Share Log…" action:@selector(share)];
    _shareLog.accessibilityIdentifier = @"galaxypad.report.share";
    _shareLog.enabled = NO;
    [stack addArrangedSubview:_shareLog];
    _openGitHub = [self buttonWithTitle:@"Open GitHub Draft" action:@selector(openGitHub)];
    _openGitHub.accessibilityIdentifier = @"galaxypad.report.github";
    _openGitHub.enabled = GalaxyPadDiagnosticsIssueURL(_draft) != nil;
    [stack addArrangedSubview:_openGitHub];
  } else {
    NSError *error = nil;
    _logText = [NSString stringWithContentsOfURL:_reportURL encoding:NSUTF8StringEncoding error:&error];
    self.navigationItem.rightBarButtonItem = [[UIBarButtonItem alloc]
      initWithBarButtonSystemItem:UIBarButtonSystemItemAction target:self action:@selector(share)];
    self.navigationItem.rightBarButtonItem.enabled = _logText != nil;
    self.navigationItem.rightBarButtonItem.accessibilityLabel = @"Share reviewed diagnostic log";
    self.navigationItem.rightBarButtonItem.accessibilityIdentifier = @"galaxypad.report.share";
  }
  [self updatePreview];
}
- (void)updatePreview {
  if (!_draft) {
    _preview.text = _logText ?: @"The local log could not be read. Close this screen and generate it again.";
    return;
  }
  NSString *text = [NSString stringWithFormat:@"%@\n\n%@", _draft[@"title"], _draft[@"body"]];
  if (_includeLog.isOn && _logText) {
    text = [text stringByAppendingFormat:@"\n\n—— Optional log (share and attach separately) ——\n%@", _logText];
  }
  _preview.text = text;
}
- (void)logChoiceChanged {
  if (_includeLog.isOn && !_logText) {
    NSError *error = nil;
    _reportURL = GalaxyPadDiagnosticsReportURL(@"user-reviewed", _answers, _technicalContext, &error);
    if (_reportURL) _logText = [NSString stringWithContentsOfURL:_reportURL encoding:NSUTF8StringEncoding error:&error];
    if (!_logText) {
      _includeLog.on = NO;
      [self showFailure:@"The diagnostic log could not be prepared. Check available storage and try again. You can still open the GitHub draft."];
    }
  }
  _shareLog.enabled = _includeLog.isOn && _logText != nil;
  [self updatePreview];
}
- (void)showFailure:(NSString *)message {
  UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Report Unavailable"
    message:message preferredStyle:UIAlertControllerStyleAlert];
  [alert addAction:[UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleDefault handler:nil]];
  [self presentViewController:alert animated:YES completion:nil];
}
- (void)close { [self dismissViewControllerAnimated:YES completion:nil]; }
- (void)share {
  if (!_reportURL || (_draft && !_includeLog.isOn)) return;
  if (![NSFileManager.defaultManager isReadableFileAtPath:_reportURL.path]) {
    [self showFailure:@"The log file is no longer available. Close this screen and prepare it again."];
    return;
  }
  UIActivityViewController *sheet = [[UIActivityViewController alloc]
    initWithActivityItems:@[_reportURL] applicationActivities:nil];
  if (_draft) {
    sheet.popoverPresentationController.sourceView = _shareLog;
    sheet.popoverPresentationController.sourceRect = _shareLog.bounds;
  } else {
    sheet.popoverPresentationController.barButtonItem = self.navigationItem.rightBarButtonItem;
  }
  [self presentViewController:sheet animated:YES completion:nil];
}
- (void)openGitHub {
  NSURL *url = GalaxyPadDiagnosticsIssueURL(_draft);
  if (!url) { [self showFailure:@"The GitHub draft could not be prepared. Close this screen and try a shorter description."]; return; }
  __weak GalaxyPadReportViewController *weakSelf = self;
  [UIApplication.sharedApplication openURL:url options:@{} completionHandler:^(BOOL success) {
    if (success) return;
    dispatch_async(dispatch_get_main_queue(), ^{
      GalaxyPadReportViewController *view = weakSelf;
      if (!view || !view.view.window) return;
      UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Could Not Open GitHub"
        message:@"Copy the draft and paste it into a new issue at github.com/chrissotraidis/galaxypad/issues. Attach any reviewed log separately."
        preferredStyle:UIAlertControllerStyleAlert];
      [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
      [alert addAction:[UIAlertAction actionWithTitle:@"Copy Draft" style:UIAlertActionStyleDefault handler:^(UIAlertAction *action) {
        (void)action;
        UIPasteboard.generalPasteboard.string = [NSString stringWithFormat:@"%@\n\n%@", view->_draft[@"title"], view->_draft[@"body"]];
      }]];
      [view presentViewController:alert animated:YES completion:nil];
    });
  }];
}
@end
