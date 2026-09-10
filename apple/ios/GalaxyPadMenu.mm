// SPDX-License-Identifier: GPL-3.0-or-later
#import "GalaxyPadMenu.h"

@implementation GalaxyPadMenu
- (instancetype)init {
  return [super initWithStyle:UITableViewStyleInsetGrouped];
}
- (void)viewDidLoad {
  [super viewDidLoad];
  self.title = @"GalaxyPad";
  self.navigationItem.rightBarButtonItem = [[UIBarButtonItem alloc]
    initWithBarButtonSystemItem:UIBarButtonSystemItemDone target:self action:@selector(close)];
}
- (void)close { if (self.onClose) self.onClose(); }
- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView { (void)tableView; return 2; }
- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  (void)tableView; return section == 0 ? 8 : 1;
}
- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
  (void)tableView; return section == 0 ? @"Controls" : @"Game Session";
}
- (NSString *)tableView:(UITableView *)tableView titleForFooterInSection:(NSInteger)section {
  (void)tableView;
  return section == 0 ? @"Classic Pointer: aim on the game view, then use A or B. The game pauses while this menu is open."
    : @"Stop exits the game. Unsaved progress will be lost; existing saves are kept.";
}
- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)index {
  (void)tableView;
  UITableViewCell *cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:nil];
  cell.selectionStyle = UITableViewCellSelectionStyleNone;
  if (index.section == 1) {
    cell.textLabel.text = @"Stop Game";
    cell.textLabel.textColor = UIColor.systemRedColor;
    cell.selectionStyle = UITableViewCellSelectionStyleDefault;
    cell.accessibilityIdentifier = @"galaxypad.menu.stop";
  } else if (index.row == 0) {
    cell.textLabel.text = @"Touch Controls";
    UISwitch *toggle = [[UISwitch alloc] init];
    toggle.on = self.touchControls;
    toggle.accessibilityLabel = @"Touch Controls";
    toggle.accessibilityIdentifier = @"galaxypad.menu.touch";
    [toggle addTarget:self action:@selector(touchChanged:) forControlEvents:UIControlEventValueChanged];
    cell.accessoryView = toggle;
  } else if (index.row == 1) {
    cell.textLabel.text = @"Opacity";
    UISlider *slider = [[UISlider alloc] initWithFrame:CGRectMake(0, 0, 150, 44)];
    slider.minimumValue = 0.2; slider.maximumValue = 1; slider.value = self.controlOpacity;
    slider.accessibilityLabel = @"Touch control opacity";
    slider.accessibilityIdentifier = @"galaxypad.menu.opacity";
    [slider addTarget:self action:@selector(opacityChanged:) forControlEvents:UIControlEventValueChanged];
    cell.accessoryView = slider;
  } else if (index.row == 4 || index.row == 6) {
    cell.textLabel.text = index.row == 4 ? @"Use Stick for Tilt" : @"Invert Tilt Y";
    UISwitch *toggle = [[UISwitch alloc] init];
    toggle.tag = index.row;
    toggle.on = index.row == 4 ? self.tiltMode : self.tiltInvertY;
    toggle.accessibilityLabel = cell.textLabel.text;
    toggle.accessibilityIdentifier = index.row == 4 ? @"galaxypad.menu.tilt" : @"galaxypad.menu.tilt-invert";
    [toggle addTarget:self action:@selector(tiltToggleChanged:) forControlEvents:UIControlEventValueChanged];
    cell.accessoryView = toggle;
  } else if (index.row == 5) {
    cell.textLabel.text = @"Tilt Sensitivity";
    UISlider *slider = [[UISlider alloc] initWithFrame:CGRectMake(0, 0, 150, 44)];
    slider.minimumValue = 0.25; slider.maximumValue = 2; slider.value = self.tiltSensitivity;
    slider.accessibilityLabel = cell.textLabel.text;
    slider.accessibilityIdentifier = @"galaxypad.menu.tilt-sensitivity";
    [slider addTarget:self action:@selector(tiltSensitivityChanged:) forControlEvents:UIControlEventValueChanged];
    cell.accessoryView = slider;
  } else if (index.row == 7) {
    cell.textLabel.text = @"Recenter Stick and Pointer";
    cell.accessibilityIdentifier = @"galaxypad.menu.recenter";
    cell.selectionStyle = UITableViewCellSelectionStyleDefault;
  } else {
    cell.textLabel.text = index.row == 2 ? @"Edit Layout" : @"Reset Layout";
    cell.selectionStyle = UITableViewCellSelectionStyleDefault;
    cell.accessibilityIdentifier = index.row == 2 ? @"galaxypad.menu.edit" : @"galaxypad.menu.reset";
  }
  if (cell.selectionStyle != UITableViewCellSelectionStyleNone) {
    cell.isAccessibilityElement = YES;
    cell.accessibilityLabel = cell.textLabel.text;
    cell.accessibilityTraits = UIAccessibilityTraitButton;
  }
  return cell;
}
- (void)touchChanged:(UISwitch *)toggle {
  self.touchControls = toggle.on;
  if (self.onTouchControls) self.onTouchControls(toggle.on);
}
- (void)tiltToggleChanged:(UISwitch *)toggle {
  if (toggle.tag == 4) self.tiltMode = toggle.on;
  else self.tiltInvertY = toggle.on;
  if (self.onTiltSettings) self.onTiltSettings(self.tiltMode, self.tiltSensitivity, self.tiltInvertY);
}
- (void)tiltSensitivityChanged:(UISlider *)slider {
  self.tiltSensitivity = slider.value;
  if (self.onTiltSettings) self.onTiltSettings(self.tiltMode, self.tiltSensitivity, self.tiltInvertY);
}
- (void)opacityChanged:(UISlider *)slider {
  self.controlOpacity = slider.value;
  if (self.onOpacity) self.onOpacity(slider.value);
}
- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)index {
  [tableView deselectRowAtIndexPath:index animated:YES];
  if (index.section == 0 && index.row == 7) {
    if (self.onRecenter) self.onRecenter();
    return;
  }
  if (index.section == 0 && index.row == 2) {
    if (self.onEditLayout) self.onEditLayout();
    return;
  }
  if (index.section == 0 && index.row == 3) {
    UIAlertController *reset = [UIAlertController alertControllerWithTitle:@"Reset Layout?"
      message:@"Touch controls will return to their default positions and sizes."
      preferredStyle:UIAlertControllerStyleAlert];
    [reset addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
    __weak GalaxyPadMenu *weakSelf = self;
    [reset addAction:[UIAlertAction actionWithTitle:@"Reset" style:UIAlertActionStyleDestructive
      handler:^(UIAlertAction *) { if (weakSelf.onResetLayout) weakSelf.onResetLayout(); }]];
    [self presentViewController:reset animated:YES completion:nil];
    return;
  }
  if (index.section != 1) return;
  UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Stop Game?"
    message:@"Unsaved progress will be lost. Existing saves will be kept."
    preferredStyle:UIAlertControllerStyleAlert];
  [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
  __weak GalaxyPadMenu *weakSelf = self;
  [alert addAction:[UIAlertAction actionWithTitle:@"Stop Game" style:UIAlertActionStyleDestructive
    handler:^(UIAlertAction *) { if (weakSelf.onStop) weakSelf.onStop(); }]];
  [self presentViewController:alert animated:YES completion:nil];
}
@end
