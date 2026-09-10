// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "GalaxyPadInput.h"
#include "InputCommon/ControllerInterface/CoreDevice.h"
#include <memory>

namespace galaxypad {
// Normal Dolphin input-device boundary, patterned after its PipeDevice. UIKit
// only touches the locked mixer. No FIFO, raw Wii report or runtime patch needed.
std::shared_ptr<ciface::Core::Device> makeInputDevice(std::shared_ptr<InputMixer> mixer);
extern const char* const mobileWiimoteConfig;
}
