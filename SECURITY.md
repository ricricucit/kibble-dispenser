# Security policy

The dispenser is a Wi-Fi device that runs unattended, so firmware security issues matter even at the prototype stage.

## Reporting a vulnerability

Please report security issues privately, not in a public issue or discussion.

1. Open the repository on GitHub and go to the "Security" tab.
2. Choose "Report a vulnerability" to open a private security advisory: https://github.com/ricricucit/kibble-dispenser/security/advisories/new
3. Describe the problem, the affected files or settings, and how to reproduce it.

You will get an answer as soon as possible. This is a hobby project, so please allow a few days. A fix is prepared in the private advisory and published together with the advisory.

## Scope

- The ESPHome configuration in `firmware/`: Wi-Fi, API encryption, OTA updates, the fallback hotspot and the handling of secrets
- Any future firmware or software in this repository
- Documentation that could lead builders into an unsafe setup (for example default passwords, or mains voltage inside the box)

Out of scope: vulnerabilities in ESPHome, Home Assistant or ESP-IDF themselves. Report those to the projects concerned.

## Supported versions

Only the latest state of the `main` branch is supported while the project is in prototype.
