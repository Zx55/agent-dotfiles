# SSH Setup

Install OpenSSH Server during Ubuntu setup so the VM can be managed without the UTM console.

## Bootstrap Access

During installation:

- select `Install OpenSSH server`
- temporarily allow SSH password authentication
- do not put the password in a command or file

After the guest boots, verify port 22 from the Mac:

```bash
nc -vz -w 3 <vm-ip> 22
```

Reuse an existing Mac SSH key when appropriate. If no key exists, create an Ed25519 key interactively:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -C "services-linux"
```

Copy the public key. Enter the Ubuntu password only at the prompt:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub <user>@<vm-ip>
```

## Add An Alias

Preserve existing `Include` directives and host blocks in `~/.ssh/config`. Add a minimal alias:

```sshconfig
Host ubuntu
    HostName <vm-ip>
    User <user>
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

Keep the file private and test the resolved configuration:

```bash
chmod 600 ~/.ssh/config
ssh -G ubuntu | grep -E '^(hostname|user|identityfile) '
ssh -o BatchMode=yes -o ConnectTimeout=5 ubuntu 'hostname; whoami'
```

## Disable Password Authentication

Only disable passwords after the key-only test succeeds in a second terminal. On Ubuntu, use a dedicated SSH configuration fragment:

```bash
ssh ubuntu 'printf "%s\n" "PasswordAuthentication no" "KbdInteractiveAuthentication no" | sudo tee /etc/ssh/sshd_config.d/90-key-only.conf >/dev/null && sudo sshd -t && sudo systemctl reload ssh'
```

Open a new connection before closing the existing session:

```bash
ssh -o BatchMode=yes ubuntu true
```

If the new connection fails, keep the UTM console open, remove `/etc/ssh/sshd_config.d/90-key-only.conf`, validate with `sudo sshd -t`, and reload SSH.

## Optional Local Alias Management

Treat `~/.ssh/config` as runtime state unless the repository already contains an authoritative SSH config source. If an existing dotfiles source owns it, edit that source and apply the normal bootstrap or link workflow instead of creating a divergent runtime-only copy.
