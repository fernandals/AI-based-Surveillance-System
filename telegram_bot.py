class TelegramBot:
    def __init__(self, token: str, surveillance_system: Any):
        self.application: Application = Application.builder().token(token).build()
        self.system: Any = surveillance_system

        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("status", self.status))
        self.application.add_handler(
            CommandHandler("sensibilidade", self.set_sensitivity)
        )
        self.application.add_handler(CommandHandler("sons", self.list_sounds))
        self.application.add_handler(
            CommandHandler("adicionar_som", self.add_sound)
        )
        self.application.add_handler(CommandHandler("remover_som", self.remove_sound))
        self.application.add_handler(CommandHandler("pausar", self.pause))
        self.application.add_handler(CommandHandler("continuar", self.resume))
        self.application.add_handler(CommandHandler("ajuda", self.help))

    async def start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await update.message.reply_text(
            "🎥 Sistema de Vigilância iniciado!\n\n"
            "Comandos disponíveis:\n"
            "/status - Ver configurações atuais\n"
            "/sensibilidade [valor] - Ajustar sensibilidade do microfone\n"
            "/sons - Listar sons monitorados\n"
            "/adicionar_som [som] - Adicionar som à lista\n"
            "/remover_som [som] - Remover som da lista\n"
            "/pausar - Pausar monitoramento\n"
            "/continuar - Retomar monitoramento\n"
            "/ajuda - Ver esta mensagem"
        )

    async def status(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        status: str = (
            f"📊 Status do Sistema:\n"
            f"    Monitoramento: {'Ativo' if self.system.monitoring_active else 'Pausado'}\n"
            f"    Sensibilidade: {self.system.mic_sensitivity}\n"
            f"    Sons monitorados: {', '.join(self.system.monitored_sounds)}"
        )
        await update.message.reply_text(status)

    async def set_sensitivity(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            value: float = float(context.args[0])
            if 0 < value <= 1:
                self.system.mic_sensitivity = value
                await update.message.reply_text(f"✅ Sensibilidade ajustada para {value}")
            else:
                await update.message.reply_text("❌ Valor deve estar entre 0 e 1")
        except (IndexError, ValueError):
            await update.message.reply_text("❌ Use: /sensibilidade [valor entre 0 e 1]")

    async def list_sounds(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        sounds: str = ", ".join(self.system.monitored_sounds)
        await update.message.reply_text(f"🔊 Sons monitorados:\n{sounds}")

    async def add_sound(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            sound: str = context.args[0].lower()
            self.system.monitored_sounds.add(sound)
            await update.message.reply_text(f"✅ Som '{sound}' adicionado à lista")
        except IndexError:
            await update.message.reply_text("❌ Use: /adicionar_som [nome do som]")

    async def remove_sound(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            sound: str = context.args[0].lower()
            if sound in self.system.monitored_sounds:
                self.system.monitored_sounds.remove(sound)
                await update.message.reply_text(f"✅ Som '{sound}' removido da lista")
            else:
                await update.message.reply_text("❌ Som não encontrado na lista")
        except IndexError:
            await update.message.reply_text("❌ Use: /remover_som [nome do som]")

    async def send_alert(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE,
        message: str, image_path: str
    ) -> None:
        try:
            await update.message.reply_photo(
                photo=image_path,
                caption=f"🚨 {message}"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Não foi possível enviar a imagem!: {e}")


    async def pause(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        self.system.monitoring_active = False
        await update.message.reply_text("⏸️ Monitoramento pausado")

    async def resume(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        self.system.monitoring_active = True
        await update.message.reply_text("▶️ Monitoramento retomado")

    async def help(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await self.start(update, context)

    def start_polling(self) -> None:
        self.application.run_polling()
