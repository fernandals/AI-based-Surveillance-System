# Guia de Configuração

## Pré-requisitos
- Raspberry Pi 3 ou superior
- Câmera compatível
- Microfone USB
- Python 3.7+

## Instalação

1. Clone o repositório:
  ```bash
  git clone https://github.com/seu-usuario/raspberry-surveillance.git
  cd raspberry-surveillance
  ```

2. Execute o script de instalação:
  ```bash
  chmod +x scripts/install_dependencies.sh
  ./scripts/install_dependencies.sh
  ```

3. Configure as variáveis de ambiente:
  ```bash
  cp .env.example .env
  nano .env  # Edite com suas configurações
  ```

## Configuração do Telegram

1. Crie um bot no Telegram
  - Converse com o @BotFather
  - Use o comando /newbot
  - Siga as instruções

2. Obtenha seu Chat ID:
  - Inicie uma conversa com seu bot
  - Acesse: https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
  - Copie o "chat_id" da resposta
  
3. Atualize o arquivo .env com suas credenciais
