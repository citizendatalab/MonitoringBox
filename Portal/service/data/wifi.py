def write_wifi_config(ap_name: str, ap_password: str):
    template = ""
    with open("wifi_template.dat", "r") as file:
        template = "".join(file.readlines())

    template = template.replace("%ap.name%", ap_name)
    template = template.replace("%ap.password%", ap_password)

    with open("/etc/hostapd/hostapd.conf", "w") as file:
        file.write(template)
