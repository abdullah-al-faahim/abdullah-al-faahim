# Design system (encrypted)

`design-system.tar.gpg` holds the private design system behind this profile, encrypted with AES-256. It opens only with the owner's passphrase.

To open it, run this in Git Bash or any shell with GPG, and type the passphrase when asked:

```bash
gpg --decrypt design-system.tar.gpg | tar -x
```

This creates a `design-system/` folder. Don't commit that folder: it is the unencrypted copy.

To save changes, pack and encrypt the folder again, then delete the unencrypted copies:

```bash
tar -cf design-system.tar design-system && gpg --symmetric --cipher-algo AES256 --output design-system.tar.gpg design-system.tar && rm -rf design-system design-system.tar
```
