// SPDX-License-Identifier: GPL-3.0-or-later
// Local preview for SunPad-derived diagnostic reports. Sharing is user initiated.
#import "GalaxyPadReportViewController.h"
@implementation GalaxyPadReportViewController {
  NSURL *_reportURL;
}
- (instancetype)initWithReportURL:(NSURL *)url {
  if ((self = [super init])) _reportURL = url;
  return self;
}
- (void)viewDidLoad {
  [super viewDidLoad];
  self.title = @"Review Diagnostic Report";
  self.view.backgroundColor = UIColor.systemBackgroundColor;
  UITextView *text = [[UITextView alloc] initWithFrame:self.view.bounds];
  text.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
  text.editable = NO;
  text.font = [UIFont monospacedSystemFontOfSize:13 weight:UIFontWeightRegular];
  text.accessibilityIdentifier = @"galaxypad.report.preview";
  NSError *error = nil;
  text.text = [NSString stringWithContentsOfURL:_reportURL encoding:NSUTF8StringEncoding error:&error];
  if (error) text.text = @"The local report could not be read. Close this screen and generate it again.";
  [self.view addSubview:text];
  self.navigationItem.leftBarButtonItem = [[UIBarButtonItem alloc]
    initWithBarButtonSystemItem:UIBarButtonSystemItemDone target:self action:@selector(close)];
  self.navigationItem.leftBarButtonItem.accessibilityLabel = @"Close diagnostic report";
  self.navigationItem.leftBarButtonItem.accessibilityIdentifier = @"galaxypad.report.close";
  self.navigationItem.rightBarButtonItem = [[UIBarButtonItem alloc]
    initWithBarButtonSystemItem:UIBarButtonSystemItemAction target:self action:@selector(share)];
  self.navigationItem.rightBarButtonItem.enabled = error == nil;
  self.navigationItem.rightBarButtonItem.accessibilityLabel = @"Share reviewed diagnostic report";
  self.navigationItem.rightBarButtonItem.accessibilityIdentifier = @"galaxypad.report.share";
}
- (void)close { [self dismissViewControllerAnimated:YES completion:nil]; }
- (void)share {
  UIActivityViewController *sheet = [[UIActivityViewController alloc]
    initWithActivityItems:@[_reportURL] applicationActivities:nil];
  sheet.popoverPresentationController.barButtonItem = self.navigationItem.rightBarButtonItem;
  [self presentViewController:sheet animated:YES completion:nil];
}
@end
