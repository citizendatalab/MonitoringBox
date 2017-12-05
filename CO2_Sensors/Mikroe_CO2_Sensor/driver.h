#include <Arduino.h>


class BoxDriver {
private:
  static BoxDriver* instance;
  const static long PROTOCOL_VERSION = 1;
  BoxDriver();
  String sensorName;
  String sensorType;
  bool hasInited;
  bool sendCommands;
  unsigned long comandCounter;
  long serialSpeed;
  void (*registerer)();
  bool packetStatus;
  void sendPacketHeader();
  void sendPacketFooter();
  void sendAttributeRaw(String *name, String *value);
  void sendStats();
  unsigned long receivedPacketCount;
  unsigned long sendPacketCount;
  unsigned long sendDataPacketCount;
  void registerListeners();
  String* searchingCommand;
  String* data;
  static void statCommandListener(String *command, String *data);
  static void helpCommandListener(String *command, String *data);
public:
  void sendAttribute(String name, String *value);
  void sendAttribute(String name, float value);
  void sendAttribute(String name, double value);
  void sendAttribute(String name, long value);
  void sendAttribute(String name, int value);
  void sendAttribute(String name, unsigned long value);
  void sendAttribute(String name, unsigned int value);
  void sendAttribute(String name, unsigned char value);
  void sendAttribute(String name, char value);
  void sendAttribute(String name, bool value);
  void sendAttribute(String name, char* value);
  void init(String name, String type, long speed, void (*registerer)());
  void tick();
  void setCommandSuccess();
  static BoxDriver* getInstance();
  void addListener(String in, void (*listener)(String*, String*));
  void callListener(String *command, String *data);
  void listCommandListeners();
};
