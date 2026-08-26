#pragma once

#include <Arduino.h>

namespace SahayakConfig {

// Change this per node before flashing. Node 1 is the base station.
constexpr uint8_t kNodeId = 2;
constexpr uint8_t kBaseStationId = 1;

// Confirm these against the purchased radio module and local operating rules.
constexpr long kLoRaFrequencyHz = 868100000L;
constexpr long kLoRaBandwidthHz = 125000L;
constexpr uint8_t kLoRaSpreadingFactor = 7;
constexpr uint8_t kLoRaCodingRateDenominator = 5;
constexpr int8_t kLoRaTxPowerDbm = 17;

// Example SPI and radio-control pins for a standard ESP32 DevKit.
constexpr int kLoRaCsPin = 5;
constexpr int kLoRaResetPin = 14;
constexpr int kLoRaDio0Pin = 26;
constexpr int kLoRaSckPin = 18;
constexpr int kLoRaMisoPin = 19;
constexpr int kLoRaMosiPin = 23;

// Example I2C/UI pins. OLED and UI modules are integrated in a later milestone.
constexpr int kOledSdaPin = 21;
constexpr int kOledSclPin = 22;
constexpr int kEmergencyButtonPin = 27;
constexpr int kGreenLedPin = 25;
constexpr int kRedLedPin = 32;
constexpr int kBuzzerPin = 13;

constexpr unsigned long kHelloIntervalMs = 10000UL;
constexpr unsigned long kAckTimeoutMs = 2500UL;
constexpr uint8_t kMaxRetries = 3;
constexpr uint8_t kInitialTtl = 8;
constexpr size_t kRadioBufferBytes = 128;

}  // namespace SahayakConfig
