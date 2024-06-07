#!/bin/bash

# Création des partitions
echo "Creationg partitions..."
parted -s /dev/sda mklabel gpt \
  mkpart primary 1MiB 500MiB \
  mkpart primary 500MiB 100% \
  set 1 esp on

# Formatage des partitions
echo "Formating partitions..."
mkfs.fat -F32 /dev/sda1
mkfs.ext4 /dev/sda2

# Montage des partitions
echo "Mounting partitions..."
mount /dev/sda2 /mnt
mkdir -p /mnt/boot/efi
mount /dev/sda1 /mnt/boot/efi

# Installation des paquets de base et de SSH
echo "Installing basic file system..."
pacstrap /mnt base linux linux-firmware base-devel sudo nano grub efibootmgr networkmanager openssh

# Configuration de l'amorçage
echo "Configuring fstab..."
genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=grub --recheck
arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg

# Configuration initiale du systeme
echo "Initial configuration system..."
arch-chroot /mnt ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime
arch-chroot /mnt hwclock --systohc
echo "en_US.UTF-8 UTF-8" >> /mnt/etc/locale.gen
arch-chroot /mnt locale-gen
echo "LANG=en_US.UTF-8" > /mnt/etc/locale.conf
echo "vm" > /mnt/etc/hostname
arch-chroot /mnt bash -c 'echo "root:123" | chpasswd'
arch-chroot /mnt useradd -m -G wheel -s /bin/bash bjill
arch-chroot /mnt bash -c 'echo "bjill:123" | chpasswd'
arch-chroot /mnt bash -c 'echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers'
arch-chroot /mnt bash -c 'echo "@includedir /etc/sudoers.d" >> /etc/sudoers'
arch-chroot /mnt systemctl enable NetworkManager
arch-chroot /mnt systemctl enable sshd


# Package utils
echo "Installing utils packages..."
arch-chroot /mnt pacman -Sy --noconfirm git curl neofetch docker docker-compose python powerline
arch-chroot /mnt systemctl enable docker
arch-chroot /mnt usermod -aG docker bjill

arch-chroot /mnt bash -c 'echo "FONT=Lat2-Terminus16" >> /etc/vconsole.conf'
arch-chroot /mnt su - bjill -c 'mkdir -p ~/.config/powerline && cp -R /usr/share/powerline/config_files/* ~/.config/powerline/'
arch-chroot /mnt su - bjill -c 'bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"'


echo "Cloning transcendance repo..."
arch-chroot /mnt su - bjill -c 'git clone /home/bjill/https://github.com/notapainting/transcendence'

#neofetch

arch-chroot /mnt su - bjill -c 'mkdir ~/.bin'
arch-chroot /mnt su - bjill -c 'touch ~/.bin/startup.sh'
arch-chroot /mnt su - bjill -c 'chmod +x ~/.bin/startup.sh'
arch-chroot /mnt su - bjill -c 'echo -e "#!/bin/bash\nneofetch" > ~/.bin/startup.sh'
arch-chroot /mnt su - bjill -c 'echo ~/.bin/startup.sh >> ~/.bashrc'


echo "Restarting..."
sleep 10
reboot
