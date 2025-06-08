#!/bin/bash
###############################################################################
##        Name: myshell_rfd.sh                                                #
##        Date: 27/07/2024                                                    #
## Description: Custom configuration for ZSH.                                 #
##----------------------------------------------------------------------------#
##      Editor: José Manuel Plana Santos                                      #
##     Contact: dev.josemanuelps@gmail.com                                    #
###############################################################################



# Script information.
scriptName="MyShell_RFD"
scriptVersion="v1.5"

# Script directories.
scriptPath=$(cd $(dirname $0) ; pwd -P)/
srcPath=$scriptPath"src/"

# Colors
red='\033[0;31m'
green='\033[0;32m'
blue='\033[0;34m'
nc='\033[0m'

# Checking binary of package manager.
if [ $(which apk 2>/dev/null | wc -l) -eq 1 ]; then
  pkgManager="sudo apk add"
  osFamily='Alpine'
elif [ $(which apt 2>/dev/null | wc -l) -eq 1 ]; then
  pkgManager="sudo apt install -y"
  osFamily='Debian'
elif [ $(which dnf 2>/dev/null | wc -l) -eq 1 ]; then
  pkgManager="sudo dnf install -y"
  osFamily='Fedora'
fi

# User information.
if [ "$EUID" -eq 0 ]; then
  execUser=$(echo -n $SUDO_USER)
else
  execUser=$(whoami)
fi
execUser_Home=$(getent passwd $execUser | cut -d: -f6)



###############################################################################
## Main code. #################################################################
###############################################################################

Main () {

  clear -x
  echo -e "Loading $scriptName $scriptVersion\n\n"

  # Directory change to the directory where the script is executed.
  cd $scriptPath

  # Process interrupt or <(CTRL + C)> combination captured.
  trap 'Catch' SIGINT

  # Checking script dependencies.
  Check_Dependencies

  # Preparing plugins
  plugins=$(egrep '^plugins=\(.*\)' $execUser_Home/.zshrc | sed 's/plugins=(//g' | sed 's/)//g')
  if [ $(egrep '^# MyShell_RFD Plugins' $execUser_Home/.zshrc | wc -l) -eq 0 ]; then
    sed -i '/^plugins=/i# The default plugins were modified by MyShell_RFD' $execUser_Home/.zshrc
    sed -i '/^plugins=/ s/^/# /' $execUser_Home/.zshrc
    sed -i '/^# plugins=/ a # MyShell_RFD Plugins' $execUser_Home/.zshrc
    sed -i "/^# MyShell_RFD Plugins/ a plugins=($plugins)" $execUser_Home/.zshrc
  fi

  # Preparing config file
  msrfdConfigFile=$execUser_Home/.myshell_rfd
  echo -e "# MyShell_RFD Config\n" >> $msrfdConfigFile

  AWS

  Bat

  CD

  Docker

  FZF

  Helm

  K

  Kubectl

  Minikube

  OC

  OpenTofu

  PLS

  PowerLevel10K
  
  Python

  Terraform

  Tridentctl

  ZSH-Autosuggestions

  ZSH-Completions

  ZSH-Syntax-Highlighthing

  # Enable plugins
  sed -i "/^plugins=/c plugins=($plugins)" $execUser_Home/.zshrc

  # Enable config file
  if [ $(egrep '.*\.myshell_rfd$' ~/.zshrc | wc -l) -eq 0 ]; then
    echo source $msrfdConfigFile >> ~/.zshrc
  fi

  if [ "$errors" != "" ]; then
    Catch
  fi

  exit 0
}


AWS () {

  if [ $(which aws 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}AWS${nc}\n###################################\n"
    read -p "Do you want to autocomplete aws commands? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  AWS" >> $msrfdConfigFile
      echo "complete -C '/usr/local/bin/aws_completer' aws" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}

Bat () {

  if [ $(which bat 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}Bat${nc}\n###################################\n"
    read -p "Do you want to replace cat command for bat command? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  Bat" >> $msrfdConfigFile
      echo "alias cat='bat'" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}

CD () {

  if [ $(which cd 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}CD${nc}\n###################################\n"
    read -p "Do you want to add cd alias? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  CD" >> $msrfdConfigFile
      echo "alias ..='cd ..'" >> $msrfdConfigFile
      echo "alias --='cd -'" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


Docker () {

  if [ $(which docker 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}Docker${nc}\n###################################\n"
    read -p "Do you want to add docker plugin? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      plugins=$plugins" docker"
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


FZF () {

  if [ ! -d $ZSH_CUSTOM/fzf ]; then
    echo -e "###################################\n# ${blue}FZF${nc}\n###################################\n"
    read -p "Do you want to install fzf plugin? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      git clone --depth 1 https://github.com/junegunn/fzf.git $ZSH_CUSTOM/fzf
      $ZSH_CUSTOM/fzf/install
      rm -f $execUser_Home/.fzf.bash
      mv $execUser_Home/.fzf.zsh $ZSH_CUSTOM/fzf
      echo "##  FZF" >> $msrfdConfigFile
      echo "[ -f ~/.oh-my-zsh/custom/fzf/.fzf.zsh ] && source ~/.oh-my-zsh/custom/fzf/.fzf.zsh" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
      sed -i '/.*fzf.*/d' $execUser_Home/.zshrc
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


Helm () {

  if [ $(which helm 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}Helm${nc}\n###################################\n"
    read -p "Do you want to autocomplete helm commands? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  Helm" >> $msrfdConfigFile
      echo "source <(helm completion zsh); compdef _helm helm" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


K () {

  if [ ! -d $ZSH_CUSTOM/plugins/k ]; then
    echo -e "###################################\n# ${blue}K${nc}\n###################################\n"
    read -p "Do you want to install custom k => z plugin? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      git clone https://github.com/supercrabtree/k $ZSH_CUSTOM/plugins/k; sed -i 's/^k[[:space:]]/z /g' $ZSH_CUSTOM/plugins/k/k.sh
      plugins=$plugins" k"
      echo "##  K" >> $msrfdConfigFile
      echo "alias f='z -ha'" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


Kubectl () {

  if [ $(which kubectl 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}Kubectl${nc}\n###################################\n"
    read -p "Do you want to autocomplete kubectl commands? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  Kubectl" >> $msrfdConfigFile
      echo "source <(kubectl completion zsh); compdef _kubectl kubectl" >> $msrfdConfigFile
      echo "compdef __start_kubectl k" >> $msrfdConfigFile
      echo "alias k=kubectl" >> $msrfdConfigFile
      echo "compdef __start_kubectl ka" >> $msrfdConfigFile
      echo "alias ka='kubectl apply -f'" >> $msrfdConfigFile
      echo "compdef __start_kubectl kc" >> $msrfdConfigFile
      echo "alias kc='kubectl create'" >> $msrfdConfigFile
      echo "compdef __start_kubectl kd" >> $msrfdConfigFile
      echo "alias kd='kubectl describe'" >> $msrfdConfigFile
      echo "compdef __start_kubectl kdc" >> $msrfdConfigFile
      echo "alias kdc='kubectl config delete-context'" >> $msrfdConfigFile
      echo "compdef __start_kubectl ke" >> $msrfdConfigFile
      echo "alias ke='kubectl exec -ti'" >> $msrfdConfigFile
      echo "compdef __start_kubectl kg" >> $msrfdConfigFile
      echo "alias kg='kubectl get'" >> $msrfdConfigFile
      echo "compdef __start_kubectl kgj" >> $msrfdConfigFile
      echo "alias kgj='kubectl get -o json'" >> $msrfdConfigFile
      echo "compdef __start_kubectl kgy" >> $msrfdConfigFile
      echo "alias kgy='kubectl get -o yaml'" >> $msrfdConfigFile
      echo "compdef __start_kubectl kl" >> $msrfdConfigFile
      echo "alias kl='kubectl logs'" >> $msrfdConfigFile
      echo "compdef __start_kubectl kn" >> $msrfdConfigFile
      echo "alias kn='kubectl config set-context --current --namespace'" >> $msrfdConfigFile
      echo "compdef __start_kubectl ku" >> $msrfdConfigFile
      echo "alias ku='kubectl config use-context'" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


Minikube () {

  if [ $(which minikube 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}Minikube${nc}\n###################################\n"
    read -p "Do you want to autocomplete minikube commands? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  Minikube" >> $msrfdConfigFile
      echo "source <(minikube completion zsh)" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


OC () {

  if [ $(which oc 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}OC${nc}\n###################################\n"
    read -p "Do you want to autocomplete oc commands? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  OC" >> $msrfdConfigFile
      echo "source <(oc completion zsh); compdef _oc oc" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}

OpenTofu () {

  if [ $(which opentofu 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}OpenTofu${nc}\n###################################\n"
    read -p "Do you want to autocomplete opentofu commands? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  OpenTofu" >> $msrfdConfigFile
      echo "complete -o nospace -C /usr/bin/opentofu opentofu" >> $msrfdConfigFile
      echo "alias ot='opentofu'" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


PLS () {

  if [ $(which sudo 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}PLS${nc}\n###################################\n"
    read -p "Do you want to add pls alias? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  PLS" >> $msrfdConfigFile
      echo "alias pls='sudo !!'" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


PowerLevel10K () {

  if [ ! -f $execUser_Home/.p10k.zsh ]; then
    echo -e "###################################\n# ${blue}PowerLevel10K${nc}\n###################################\n"
    read -p "Do you want to install powerlevel10k theme? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      git clone --depth=1 https://github.com/romkatv/powerlevel10k.git $ZSH_CUSTOM/themes/powerlevel10k
    fi

    if [ $(egrep 'powerlevel10k' $execUser_Home/.zshrc | wc -l) -eq 0 ]; then
      echo ""; read -p "Do you want to load custom powerlevel10k theme? [y/n]: " selectedOption
      if [ "$selectedOption" == "y" ]; then
        cp $srcPath/p10k.zsh $execUser_Home/.p10k.zsh
        sed -i '/^ZSH_THEME=/i# The ZSH_THEME was modified by MyShell_RFD' $execUser_Home/.zshrc
        sed -i '/^ZSH_THEME=/ s/^/# /' $execUser_Home/.zshrc
        sed -i '/^# ZSH_THEME=/ a ZSH_THEME='powerlevel10k/powerlevel10k'' $execUser_Home/.zshrc
        echo "##  PowerLevel10K" >> $msrfdConfigFile
        echo -e "[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh\n" >> $msrfdConfigFile
      fi
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


Python () {

  if [ $(which python3 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}Python3${nc}\n###################################\n"
    read -p "Do you want to create Python virtual enviroment? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  Python3" >> $msrfdConfigFile
      echo "source $execUser_Home/.py-venv-default/bin/activate" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


Terraform () {

  if [ $(which terraform 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}Terraform${nc}\n###################################\n"
    read -p "Do you want to autocomplete terraform commands? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  Terraform" >> $msrfdConfigFile
      echo "autoload -U +X bashcompinit && bashcompinit" >> $msrfdConfigFile
      echo "complete -o nospace -C /usr/bin/terraform terraform" >> $msrfdConfigFile
      echo "alias t='terraform'" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


Tridentctl () {

  if [ $(which tridentctl 2>/dev/null | wc -l) -eq 1 ]; then
    echo -e "###################################\n# ${blue}Tridentctl${nc}\n###################################\n"
    read -p "Do you want to autocomplete tridentctl commands? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      echo "##  Tridentctl" >> $msrfdConfigFile
      echo "source <(tridentctl completion zsh); compdef _tridentctl tridentctl" >> $msrfdConfigFile
      echo "compdef __start_tridentctl astra" >> $msrfdConfigFile
      echo "alias astra='tridentctl -n trident'" >> $msrfdConfigFile
      echo "" >> $msrfdConfigFile
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


ZSH-Autosuggestions () {

  if [ ! -d $ZSH_CUSTOM/plugins/zsh-autosuggestions ]; then
    echo -e "###################################\n# ${blue}ZSH-Autosuggestions${nc}\n###################################\n"
    read -p "Do you want to install ZSH-Autosuggestions plugin? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      git clone https://github.com/zsh-users/zsh-autosuggestions $ZSH_CUSTOM/plugins/zsh-autosuggestions
      plugins=$plugins" zsh-autosuggestions"
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


ZSH-Completions () {

  if [ ! -d $ZSH_CUSTOM/plugins/zsh-completions ]; then
    echo -e "###################################\n# ${blue}ZSH-Completions${nc}\n###################################\n"
    read -p "Do you want to install ZSH-Completions plugin? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      git clone https://github.com/zsh-users/zsh-completions $ZSH_CUSTOM/plugins/zsh-completions
      plugins=$plugins" zsh-completions"
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}


ZSH-Syntax-Highlighthing () {

  if [ ! -d $ZSH_CUSTOM/plugins/zsh-syntax-highlighting ]; then
    echo -e "###################################\n# ${blue}ZSH-Syntax-Highlighthing${nc}\n###################################\n"
    read -p "Do you want to install ZSH-Syntax-Highlighthing plugin? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      git clone https://github.com/zsh-users/zsh-syntax-highlighting.git $ZSH_CUSTOM/plugins/zsh-syntax-highlighting
      plugins=$plugins" zsh-syntax-highlighting"
    fi
    echo -e "${green}Done!${nc}\n\n"
  fi
}



###############################################################################
## Auxiliary methods. #########################################################
###############################################################################

# Process interrupt or <(CTRL + C)> combination captured.
Catch () {

  clear -x

  if [ "$errors" != "" ]; then
    echo -e "${red}[ERROR LOGS]\n$errors${nc}"
    exit 1
  fi

  echo -e "${red}The script $scriptName has been forced to close!"
  exit 1
}

# Checking script dependencies.
Check_Dependencies () {

  echo -e "###################################\n# ${blue}Checking dependencies${nc}\n###################################"

  # Checking 'curl' binary.
  checkBin=$(which curl 2>/dev/null | wc -l)
  if [ $checkBin -eq 0 ]; then

    echo "Trying to install curl..."
    $pkgManager curl

    checkBin=$(which curl 2>/dev/null | wc -l)
    if [ $checkBin -eq 0 ]; then
      errors=$errors"[curl] Not curl binary found. Please install it manually and try again.\n"
      Catch
    fi
  fi

  # Checking 'git' binary.
  checkBin=$(which git 2>/dev/null | wc -l)
  if [ $checkBin -eq 0 ]; then

    echo "Trying to install git..."
    $pkgManager git

    checkBin=$(which git 2>/dev/null | wc -l)
    if [ $checkBin -eq 0 ]; then
      errors=$errors"[git] Not git binary found. Please install it manually and try again.\n"
      Catch
    fi
  fi

  # Checking 'zsh' binary.
  checkBin=$(which zsh 2>/dev/null | wc -l)
  if [ $checkBin -eq 0 ]; then

    echo "Trying to install zsh..."
    $pkgManager zsh

    read -p "Do you want to setup zsh as default shell? [y/n]: " selectedOption
    if [ "$selectedOption" == "y" ]; then
      chsh -s $(which zsh)
    fi    

    checkBin=$(which zsh 2>/dev/null | wc -l)
    if [ $checkBin -eq 0 ]; then
      errors=$errors"[zsh] Not zsh binary found. Please install it manually and try again.\n"
      Catch
    fi
  fi

  # Checking 'oh-my-zsh' directory.
  checkDir=$execUser_Home/.oh-my-zsh
  if [ ! -d $checkDir ]; then

    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    ZSH_CUSTOM=$execUser_Home'/.oh-my-zsh/custom'

    if [ ! -d $checkDir ]; then
      errors=$errors"[oh-my-zsh] Not zsh binary found. Please install it manually and try again.\n"
      Catch
    fi
  fi
  ZSH_CUSTOM=$execUser_Home'/.oh-my-zsh/custom'

  echo -e "${green}Done!${nc}\n\n"
}



###############################################################################
## Execution. #################################################################
###############################################################################

# Script execution start.
Main


