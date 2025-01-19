#!/bin/bash

# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependências do sistema
sudo apt-get install -y \
    python3-pip \
    libportaudio2 \
    python3-opencv \
    python3-venv

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install -r requirements.txt