// SPDX-License-Identifier: GPL-3.0-or-later
#import "GalaxyPadAboutViewController.h"
@implementation GalaxyPadAboutViewController
- (void)viewDidLoad {
  [super viewDidLoad];
  self.title=@"About GalaxyPad";
  self.view.backgroundColor=UIColor.systemBackgroundColor;
  UITextView *text=[[UITextView alloc] init];
  text.translatesAutoresizingMaskIntoConstraints=NO;
  text.editable=NO;
  text.font=[UIFont preferredFontForTextStyle:UIFontTextStyleBody];
  text.adjustsFontForContentSizeCategory=YES;
  text.textContainerInset=UIEdgeInsetsMake(20,20,24,20);
  text.accessibilityIdentifier=@"galaxypad.about.text";
  NSString *version=[NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleShortVersionString"] ?: @"Unknown";
  NSString *build=[NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleVersion"] ?: @"Unknown";
  text.text=[NSString stringWithFormat:
    @"GalaxyPad %@ (%@)\nPrivate development build\n\n"
    "Compatibility\nSuper Mario Galaxy — RMGE01, revision 0. Gameplay, performance and device validation are still in progress.\n\n"
    "Credits\nSunPad — native Apple UI and touch-control foundation.\n"
    "ModernGekko and Dolphin/RecompCore — runtime and emulated hardware.\n"
    "DolRecomp — ahead-of-time code generation.\n"
    "WIT — development image tooling.\n\n"
    "Third-party notices\nGalaxyPad integration source uses GPL-3.0-or-later. Dependencies retain their own licenses and per-file notices. The complete bundled license and corresponding-source audit is not finished; this screen is not a substitute for those notices.\n\n"
    "Rights and distribution\nSuper Mario Galaxy and Nintendo names and game content belong to their respective rights holders. GalaxyPad is not affiliated with or endorsed by Nintendo. Game content is not licensed under GalaxyPad's source license.\n\n"
    "This build is for private local development. Public distribution of this app or its generated game module is not approved. Do not share game images, extracted assets, generated game code, saves or NAND data.",version,build];
  [self.view addSubview:text];
  UILayoutGuide *safe=self.view.safeAreaLayoutGuide;
  [NSLayoutConstraint activateConstraints:@[
    [text.leadingAnchor constraintEqualToAnchor:safe.leadingAnchor],
    [text.trailingAnchor constraintEqualToAnchor:safe.trailingAnchor],
    [text.topAnchor constraintEqualToAnchor:safe.topAnchor],
    [text.bottomAnchor constraintEqualToAnchor:safe.bottomAnchor]]];
  self.navigationItem.rightBarButtonItem=[[UIBarButtonItem alloc]
    initWithBarButtonSystemItem:UIBarButtonSystemItemDone target:self action:@selector(close)];
  self.navigationItem.rightBarButtonItem.accessibilityIdentifier=@"galaxypad.about.close";
}
- (void)close { [self dismissViewControllerAnimated:YES completion:nil]; }
@end
