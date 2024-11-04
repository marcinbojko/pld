# Changelog "prepare_linux_desktop" ansible role

## Version 1.1.0 [2024-11-04]

* [OS] - added support for Linux Mint 22.x. Using official Mint 22.x `mintupgrade` package, running this playbook afterwards creates a fully functional desktop environment.
* [BREAKING CHANGES] - until further notice, Zorin OS is not supported in this version of release due to changes in base distro. This makes release 1.0.3 Zorin-OS compatible.
* [DEB] upgraded `tabby` to 1.0.215
* [DEB] upgraded `balena-etcher` to 1.19.25
* [DEB] upgraded `kube-bench` to 0.9.1
* [DEB] upgraded `syft` to 1.15.0
* [DEB] upgraded `steampipe` to 1.0.0
* [DEB] upgraded `rambox` to 2.4.1
* [DEB] upgraded `sops` to 3.9.1
* [DEB] upgraded `insync` to 3.9.4.60020
* [DEB] upgraded `wave` to 0.9.1
* [PACKAGES] added `trippy` [https://github.com/fujiapple852/trippy](https://github.com/fujiapple852/trippy)
* [PACKAGES] added `lazydocker` [https://github.com/jesseduffield/lazydocker](https://github.com/jesseduffield/lazydocker)
* [PACKAGES] upgrade `amass` to version 4.2.0
* [PACKAGES] upgrade `act` to 2.0.69
* [PACKAGES] upgrade `argo` to 2.12.6
* [PACKAGES] upgrade `eza` to 0.20.6
* [PACKAGES] upgrade `k3s` to v1.31.2+k3s1
* [PACKAGES] upgrade `kubent` to nightly-0.7.3-31-g2e643a7
* [PACKAGES] upgrade `kustomize` to 5.5.0
* [PACKAGES] upgrade `polaris` to 9.5.0
* [PACKAGES] added `infisical` [https://github.com/Infisical/infisical](https://github.com/Infisical/infisical)
* [PACKAGES] added `axiom` [https://github.com/axiomhq/cli](https://github.com/axiomhq/cli)
* [DEB] added `wave` package [https://www.waveterm.dev/download](https://www.waveterm.dev/download)
* [PACKAGES] added `solaar` package as optional package for Logitech devices


## Version 1.0.2 [2024-07-05]

* fixed `teller` package being inproperly unarchived
* fixed missing owner on unarchived files (assigned to root instead of `pld_active_user`)
* [VSCODE] removed `infracost.infracost` from extensions list
* [DEB] upgraded `insync` to version 3.9.2.60014ś

## Version 1.0.1 [2024-07-05]

* [DEB] added `duf` [https://github.com/muesli/duf](https://github.com/muesli/duf)
* [PACKAGES] added `eza` [https://github.com/eza-community/eza](https://github.com/eza-community/eza)
* [PACKAGES] upgraded `act` to version 0.2.64
* [PACKAGES] upgraded `k3d` to version 5.7.
* [PACKAGES] upgraded `k3s` to version 1.30.2+k3s1
* [PACKAGES] upgraded `k3sup` to version 0.13.6
* [DEB] upgraded `k9s` to version  0.32.5
* [DEB] upgraded `kube-bench` to version 0.8.0
* [PACKAGES] upgraded `nerdctl` to version 1.7.6
* [PACKAGES] upgraded `polaris` to version 9.1.1
* [DEB] upgrade `rambox` to version 2.3.4
* [DEB] upgraded `sops` to version 3.9.0
* [DEB] upgraded `steampipe` to version 0.23.2
* [PACKAGES] upgraded `teller` to version 2.0.7
* [DEB] upgraded `tabby` to version 1.0.208
* [PACKAGES] upgraded `tflint` to version 0.51.2
* [PACKAGES] upgraded `yq` to version 4.44.2
* [FLATPAK] added `Insomnia` as API Client

## Version 1.0.0 [2024-07-02]

* inital Version
