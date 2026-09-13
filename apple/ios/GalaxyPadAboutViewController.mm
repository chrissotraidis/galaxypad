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
  text.selectable=YES;
  text.font=[UIFont preferredFontForTextStyle:UIFontTextStyleBody];
  text.adjustsFontForContentSizeCategory=YES;
  text.textContainerInset=UIEdgeInsetsMake(20,20,24,20);
  text.accessibilityIdentifier=@"galaxypad.about.text";
  NSString *version=[NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleShortVersionString"] ?: @"Unknown";
  NSString *build=[NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleVersion"] ?: @"Unknown";
  text.text=[NSString stringWithFormat:
    @"GalaxyPad %@ (%@)\nExperimental preview\n\n"
    "Compatibility\nSuper Mario Galaxy — RMGE01, revision 0. Gameplay, performance and device validation are still in progress.\n\n"
    "Built on upstream work\nModernGekko — runtime integration and game-port tooling.\n"
    "DolRecomp — ahead-of-time PowerPC code generation.\n"
    "RecompCore — Dolphin-derived recompilation runtime.\n"
    "Dolphin — Wii hardware, graphics, audio and input.\n"
    "SunPad — Apple UI and touch-control foundation.\n"
    "Wiimms ISO Tools — development image tooling.\n\n"
    "GalaxyPad adds Apple platform integration and controls. See the credits for contributors and details of AI assistance in GalaxyPad development and artwork.\n\n"
    "Credits and artwork provenance\nThird-party notices\n\n"
    "GalaxyPad integration source uses GPL-3.0-or-later. Dependencies retain their own licenses and per-file notices.\n\n"
    "Rights and distribution\nSuper Mario Galaxy and Nintendo names and game content belong to their respective rights holders. GalaxyPad is not affiliated with or endorsed by Nintendo. Game content is not licensed under GalaxyPad's source license.\n\n"
    "Supply your own supported game image. Do not request or share game images, extracted assets, saves or NAND data in project channels.",version,build];
  NSMutableAttributedString *content=[[NSMutableAttributedString alloc]
    initWithString:text.text attributes:@{NSFontAttributeName:text.font,
      NSForegroundColorAttributeName:UIColor.labelColor}];
  NSDictionary<NSString *,NSString *> *links=@{
    @"ModernGekko":@"https://github.com/ExpansionPak/ModernGekko",
    @"DolRecomp":@"https://github.com/ExpansionPak/DolRecomp",
    @"RecompCore":@"https://github.com/ExpansionPak/RecompCore",
    @"Dolphin —":@"https://github.com/dolphin-emu/dolphin",
    @"SunPad":@"https://github.com/chrissotraidis/sunpad",
    @"Wiimms ISO Tools":@"https://wit.wiimm.de/",
    @"Credits and artwork provenance":@"https://github.com/chrissotraidis/galaxypad/blob/main/CREDITS.md",
    @"Third-party notices":@"https://github.com/chrissotraidis/galaxypad/blob/main/THIRD-PARTY-NOTICES.md"
  };
  for (NSString *label in links)
    [content addAttribute:NSLinkAttributeName value:[NSURL URLWithString:links[label]]
      range:[content.string rangeOfString:label]];
  text.attributedText=content;
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
