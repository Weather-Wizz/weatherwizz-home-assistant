# WeatherWizz for Home Assistant

Connect your WeatherWizz account to Home Assistant and expose the stations and
sensors permitted by your WeatherWizz Home Assistant key.

## Install with HACS

1. Open **HACS → Integrations** in Home Assistant.
2. Open the menu in the top-right corner and choose **Custom repositories**.
3. Add `https://github.com/Weather-Wizz/weatherwizz-home-assistant` as an
   **Integration** repository.
4. Search for **WeatherWizz**, choose **Download**, and restart Home Assistant
   when HACS asks you to.
5. In WeatherWizz, open **Home Assistant**, create a key, and copy it.
6. In Home Assistant, open
   **Settings → Devices & services → Add integration → WeatherWizz**.
7. Enter the API address displayed by WeatherWizz and paste the key.

## Install manually

1. Download the repository source and open the `custom_components` folder.
2. Using the Home Assistant Samba Share, File Editor, or Studio Code Server
   add-on, copy the complete `weatherwizz` folder into
   `/config/custom_components/`.
3. Confirm that `/config/custom_components/weatherwizz/manifest.json` and
   `/config/custom_components/weatherwizz/__init__.py` exist. Do not leave the
   folder nested as
   `/config/custom_components/weatherwizz/weatherwizz`.
4. Restart Home Assistant.
5. Follow steps 5–7 in the HACS instructions above to connect WeatherWizz.

## Access and refresh behaviour

The WeatherWizz key controls which stations and sensors Home Assistant receives.
Changes made to key access in WeatherWizz take effect on the next Home Assistant
refresh. The default refresh interval is 60 seconds and can be changed from the
integration options in Home Assistant.

## Support

For help with WeatherWizz, visit
[WeatherWizz Support](https://www.weatherwizz.com/contact/).
