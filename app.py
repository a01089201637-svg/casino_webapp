import random
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'casino_secret_key_12345'

# Initialize session balance
@app.before_request
def make_session_permanent():
    session.permanent = True
    if 'balance' not in session:
        session['balance'] = 10000 # Default starting chips: $10,000

@app.route('/')
def index():
    return render_template('index.html', balance=session['balance'])

@app.route('/api/reset-balance', methods=['POST'])
def reset_balance():
    session['balance'] = 10000
    return jsonify({'status': 'success', 'balance': session['balance']})

# --- 1. ROULETTE ---
@app.route('/api/roulette/play', methods=['POST'])
def play_roulette():
    data = request.json
    bet_type = data.get('bet_type')  # 'number', 'red', 'black', 'even', 'odd', 'high', 'low'
    bet_value = data.get('bet_value') # e.g. 7 or 'red'
    bet_amount = int(data.get('bet_amount', 0))

    if bet_amount <= 0 or bet_amount > session['balance']:
        return jsonify({'error': 'Invalid bet amount'}), 400

    # European Roulette numbers 0-36
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    winning_number = random.randint(0, 36)
    
    color = 'green' if winning_number == 0 else ('red' if winning_number in red_numbers else 'black')
    
    payout_multiplier = 0
    win = False

    if bet_type == 'number' and int(bet_value) == winning_number:
        payout_multiplier = 35
        win = True
    elif winning_number != 0:
        if bet_type == 'red' and color == 'red':
            payout_multiplier = 1
            win = True
        elif bet_type == 'black' and color == 'black':
            payout_multiplier = 1
            win = True
        elif bet_type == 'even' and winning_number % 2 == 0:
            payout_multiplier = 1
            win = True
        elif bet_type == 'odd' and winning_number % 2 != 0:
            payout_multiplier = 1
            win = True
        elif bet_type == 'low' and 1 <= winning_number <= 18:
            payout_multiplier = 1
            win = True
        elif bet_type == 'high' and 19 <= winning_number <= 36:
            payout_multiplier = 1
            win = True

    if win:
        winnings = bet_amount * payout_multiplier
        session['balance'] += winnings
        net_change = winnings
    else:
        session['balance'] -= bet_amount
        net_change = -bet_amount

    return jsonify({
        'winning_number': winning_number,
        'color': color,
        'win': win,
        'net_change': net_change,
        'balance': session['balance']
    })

# --- 2. CRAPS ---
@app.route('/api/craps/play', methods=['POST'])
def play_craps():
    data = request.json
    bet_amount = int(data.get('bet_amount', 0))
    action = data.get('action') # 'roll' or 'reset_point'
    
    if bet_amount <= 0 or bet_amount > session['balance']:
        return jsonify({'error': 'Invalid bet amount'}), 400

    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    dice_sum = dice1 + dice2
    
    point = session.get('craps_point', None)
    result_status = '' # 'win', 'lose', 'point_set', 'continue'
    net_change = 0

    if point is None: # Come-out Roll
        if dice_sum in [7, 11]:
            result_status = 'win'
            net_change = bet_amount
            session['balance'] += bet_amount
        elif dice_sum in [2, 3, 12]:
            result_status = 'lose'
            net_change = -bet_amount
            session['balance'] -= bet_amount
        else:
            result_status = 'point_set'
            session['craps_point'] = dice_sum
            point = dice_sum
    else: # Point Stage
        if dice_sum == point:
            result_status = 'win'
            net_change = bet_amount
            session['balance'] += bet_amount
            session['craps_point'] = None
        elif dice_sum == 7:
            result_status = 'lose'
            net_change = -bet_amount
            session['balance'] -= bet_amount
            session['craps_point'] = None
        else:
            result_status = 'continue'

    return jsonify({
        'dice1': dice1,
        'dice2': dice2,
        'dice_sum': dice_sum,
        'status': result_status,
        'point': session.get('craps_point', None),
        'net_change': net_change,
        'balance': session['balance']
    })

# --- 3. SLOT MACHINE ---
@app.route('/api/slots/play', methods=['POST'])
def play_slots():
    data = request.json
    bet_amount = int(data.get('bet_amount', 0))

    if bet_amount <= 0 or bet_amount > session['balance']:
        return jsonify({'error': 'Invalid bet amount'}), 400

    symbols = ['🍒', '🍋', '🔔', '💎', '7️⃣', '🃏'] # 🃏 = Wild
    weights = [30, 25, 20, 15, 8, 2] # Probabilities

    reel1 = random.choices(symbols, weights=weights)[0]
    reel2 = random.choices(symbols, weights=weights)[0]
    reel3 = random.choices(symbols, weights=weights)[0]

    reels = [reel1, reel2, reel3]
    
    # Calculate payout
    multiplier = 0
    # Wild logic
    non_wilds = [s for s in reels if s != '🃏']
    
    if len(non_wilds) == 0: # All 3 Wilds
        multiplier = 100
    elif len(set(non_wilds)) == 1: # 3 match (with wild assistance)
        match_symbol = non_wilds[0]
        payouts = {'🍒': 5, '🍋': 10, '🔔': 20, '💎': 50, '7️⃣': 80}
        multiplier = payouts.get(match_symbol, 5)
    elif reels.count('🃏') == 1 and len(set(non_wilds)) == 2: # 2 match + 1 wild
        multiplier = 2
    else:
        # Check standard 2 match
        if reel1 == reel2 or reel2 == reel3 or reel1 == reel3:
            multiplier = 2

    if multiplier > 0:
        winnings = bet_amount * multiplier
        session['balance'] += winnings
        net_change = winnings
        win = True
    else:
        session['balance'] -= bet_amount
        net_change = -bet_amount
        win = False

    return jsonify({
        'reels': reels,
        'win': win,
        'multiplier': multiplier,
        'net_change': net_change,
        'balance': session['balance']
    })

# --- 4. DREAM CATCHER / BIG WHEEL ---
@app.route('/api/dreamcatcher/play', methods=['POST'])
def play_dreamcatcher():
    data = request.json
    bet_target = str(data.get('target')) # '1', '2', '5', '10', '20', '40'
    bet_amount = int(data.get('bet_amount', 0))

    if bet_amount <= 0 or bet_amount > session['balance']:
        return jsonify({'error': 'Invalid bet amount'}), 400

    # 54 segments wheel
    wheel_segments = [
        '1','2','1','5','1','2','1','10','1','2','1','5','1','2','1','2x',
        '1','2','1','5','1','2','1','20','1','2','1','5','1','2','1','7x',
        '1','2','1','5','1','2','1','10','1','2','1','5','1','2','1','40',
        '1','2','1','5','1','2'
    ]
    
    hit_segment = random.choice(wheel_segments)
    
    win = False
    multiplier = 0
    
    if hit_segment == bet_target:
        win = True
        multiplier = int(bet_target)
    elif hit_segment in ['2x', '7x']:
        # Simple bonus multiplier handling: return original bet + bonus credit
        win = True
        multiplier = int(hit_segment.replace('x', ''))

    if win:
        winnings = bet_amount * multiplier
        session['balance'] += winnings
        net_change = winnings
    else:
        session['balance'] -= bet_amount
        net_change = -bet_amount

    return jsonify({
        'hit_segment': hit_segment,
        'win': win,
        'multiplier': multiplier,
        'net_change': net_change,
        'balance': session['balance']
    })

# --- 5. SIC BO ---
@app.route('/api/sicbo/play', methods=['POST'])
def play_sicbo():
    data = request.json
    bet_type = data.get('bet_type') # 'big', 'small', 'triple', 'single'
    bet_value = data.get('bet_value') # For single (1-6) or specific triple
    bet_amount = int(data.get('bet_amount', 0))

    if bet_amount <= 0 or bet_amount > session['balance']:
        return jsonify({'error': 'Invalid bet amount'}), 400

    dice = [random.randint(1, 6) for _ in range(3)]
    dice_sum = sum(dice)
    is_triple = (dice[0] == dice[1] == dice[2])

    win = False
    multiplier = 0

    if bet_type == 'small':
        if 4 <= dice_sum <= 10 and not is_triple:
            win = True
            multiplier = 1
    elif bet_type == 'big':
        if 11 <= dice_sum <= 17 and not is_triple:
            win = True
            multiplier = 1
    elif bet_type == 'triple':
        if is_triple:
            if bet_value == 'any' or int(bet_value) == dice[0]:
                win = True
                multiplier = 150
    elif bet_type == 'single':
        target_num = int(bet_value)
        match_count = dice.count(target_num)
        if match_count > 0:
            win = True
            multiplier = match_count # 1x for 1 dice, 2x for 2 dice, 3x for 3 dice

    if win:
        winnings = bet_amount * multiplier
        session['balance'] += winnings
        net_change = winnings
    else:
        session['balance'] -= bet_amount
        net_change = -bet_amount

    return jsonify({
        'dice': dice,
        'dice_sum': dice_sum,
        'is_triple': is_triple,
        'win': win,
        'net_change': net_change,
        'balance': session['balance']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)