import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

games = {}

def create_board():
    return [['⬜' for _ in range(3)] for _ in range(3)]

def board_to_text(board):
    text = ""
    for row in board:
        text += "".join(row) + "\n"
    return text

def check_winner(board):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != '⬜':
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != '⬜':
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != '⬜':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != '⬜':
        return board[0][2]
    return None

def is_full(board):
    for row in board:
        if '⬜' in row:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 **Крестики-Нолики!**\n\n"
        "Команды:\n"
        "/game - Начать новую игру\n"
        "/help - Помощь"
    )

async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    games[user_id] = {
        'board': create_board(),
        'player': '❌',
        'active': True
    }    
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append(InlineKeyboardButton("⬜", callback_data=f"move_{i}_{j}"))
        keyboard.append(row)
    
    await update.message.reply_text(
        "🎮 **Новая игра!**\n\n" + board_to_text(games[user_id]['board']) + "\nТвой ход: ❌",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if user_id not in games:
        await query.edit_message_text("❌ Начни игру командой /game")
        return
    
    game = games[user_id]
    if not game['active']:
        await query.edit_message_text("❌ Игра окончена! Начни новую: /game")
        return
    
    data = query.data.split("_")
    row, col = int(data[1]), int(data[2])
    
    if game['board'][row][col] != '⬜':
        await query.answer("❌ Клетка занята!", show_alert=True)
        return
    
    game['board'][row][col] = game['player']
    
    winner = check_winner(game['board'])
    if winner:
        game['active'] = False
        keyboard = [[InlineKeyboardButton("🔄 Новая игра", callback_data="newgame")]]
        await query.edit_message_text(
            f"🏆 **Победа {winner}!**\n\n" + board_to_text(game['board']),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    if is_full(game['board']):
        game['active'] = False
        keyboard = [[InlineKeyboardButton("🔄 Новая игра", callback_data="newgame")]]
        await query.edit_message_text(            "🤝 **Ничья!**\n\n" + board_to_text(game['board']),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    game['player'] = '⭕' if game['player'] == '❌' else '❌'
    
    import random
    empty_cells = [(i, j) for i in range(3) for j in range(3) if game['board'][i][j] == '⬜']
    if empty_cells:
        bot_row, bot_col = random.choice(empty_cells)
        game['board'][bot_row][bot_col] = game['player']
    
    winner = check_winner(game['board'])
    if winner:
        game['active'] = False
        keyboard = [[InlineKeyboardButton("🔄 Новая игра", callback_data="newgame")]]
        await query.edit_message_text(
            f"🏆 **Победа {winner}!**\n\n" + board_to_text(game['board']),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    if is_full(game['board']):
        game['active'] = False
        keyboard = [[InlineKeyboardButton("🔄 Новая игра", callback_data="newgame")]]
        await query.edit_message_text(
            "🤝 **Ничья!**\n\n" + board_to_text(game['board']),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    game['player'] = '❌' if game['player'] == '⭕' else '❌'
    
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = game['board'][i][j]
            row.append(InlineKeyboardButton(cell, callback_data=f"move_{i}_{j}"))
        keyboard.append(row)
    
    await query.edit_message_text(
        board_to_text(game['board']) + f"\nТвой ход: ❌",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def new_game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()    user_id = update.effective_user.id
    
    games[user_id] = {
        'board': create_board(),
        'player': '❌',
        'active': True
    }
    
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append(InlineKeyboardButton("⬜", callback_data=f"move_{i}_{j}"))
        keyboard.append(row)
    
    await query.edit_message_text(
        "🎮 **Новая игра!**\n\n" + board_to_text(games[user_id]['board']) + "\nТвой ход: ❌",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 **Помощь**\n\n"
        "/game - Начать новую игру\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n\n"
        "Нажимай на клетки чтобы сделать ход!"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("game", new_game))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(CallbackQueryHandler(new_game_callback, pattern="^newgame$"))
    
    print("🎮 Бот Крестики-Нолики запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
