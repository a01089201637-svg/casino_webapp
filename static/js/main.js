// Sidebar Navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.game-panel').forEach(p => p.classList.remove('active'));
        
        btn.classList.add('active');
        const gameId = btn.getAttribute('data-game');
        document.getElementById(`game-${gameId}`).classList.add('active');
    });
});

// Reset Balance
document.getElementById('reset-btn').addEventListener('click', async () => {
    const res = await fetch('/api/reset-balance', { method: 'POST' });
    const data = await res.json();
    updateBalance(data.balance);
    alert('칩이 $10,000로 재충전되었습니다!');
});

function updateBalance(newBalance) {
    document.getElementById('user-balance').innerText = `$${newBalance.toLocaleString()}`;
}

// 1. ROULETTE LOGIC
async function playRoulette(betType, betValue) {
    const betAmount = document.getElementById('roulette-bet-amount').value;
    
    const res = await fetch('/api/roulette/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bet_type: betType, bet_value: betValue, bet_amount: betAmount })
    });
    
    const data = await res.json();
    if (res.status !== 200) return alert(data.error);

    // Visual Animation Effect
    const wheel = document.getElementById('roulette-wheel');
    const resultNum = document.getElementById('roulette-result-number');
    
    wheel.style.transform = 'rotate(720deg)';
    resultNum.innerText = '...';
    
    setTimeout(() => {
        wheel.style.transform = 'rotate(0deg)';
        resultNum.innerText = data.winning_number;
        resultNum.style.color = data.color === 'red' ? '#e74c3c' : (data.color === 'black' ? '#fff' : '#2ecc71');
        
        const status = document.getElementById('roulette-status');
        if (data.win) {
            status.innerHTML = `🎉 당첨! 당첨 번호: <strong>${data.winning_number} (${data.color.toUpperCase()})</strong> | 획득: +$${data.net_change.toLocaleString()}`;
            status.style.borderLeftColor = '#2ecc71';
        } else {
            status.innerHTML = `❌ 낙첨... 당첨 번호: <strong>${data.winning_number} (${data.color.toUpperCase()})</strong> | 손실: -$${Math.abs(data.net_change).toLocaleString()}`;
            status.style.borderLeftColor = '#e74c3c';
        }
        updateBalance(data.balance);
    }, 500);
}

function playRouletteSingle() {
    const val = document.getElementById('roulette-single-num').value;
    if (val === '' || val < 0 || val > 36) return alert('0에서 36 사이의 숫자를 입력하세요.');
    playRoulette('number', val);
}

// 2. CRAPS LOGIC
async function playCraps() {
    const betAmount = document.getElementById('craps-bet-amount').value;
    
    const res = await fetch('/api/craps/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bet_amount: betAmount })
    });

    const data = await res.json();
    if (res.status !== 200) return alert(data.error);

    document.getElementById('dice1').innerText = data.dice1;
    document.getElementById('dice2').innerText = data.dice2;
    document.getElementById('craps-point-display').innerText = data.point ? data.point : '없음';

    const status = document.getElementById('craps-status');
    if (data.status === 'win') {
        status.innerHTML = `🎉 승리! 주사위 합: <strong>${data.dice_sum}</strong> | 획득: +$${data.net_change.toLocaleString()}`;
        status.style.borderLeftColor = '#2ecc71';
    } else if (data.status === 'lose') {
        status.innerHTML = `❌ 패배... 주사위 합: <strong>${data.dice_sum}</strong> | 손실: -$${Math.abs(data.net_change).toLocaleString()}`;
        status.style.borderLeftColor = '#e74c3c';
    } else if (data.status === 'point_set') {
        status.innerHTML = `📌 Point 설정됨: <strong>${data.point}</strong>! 7이 나오기 전에 ${data.point}를 한 번 더 뽑으세요.`;
        status.style.borderLeftColor = '#f39c12';
    } else {
        status.innerHTML = `🎲 주사위 합: <strong>${data.dice_sum}</strong>. 계속해서 Point(${data.point})를 노려보세요!`;
        status.style.borderLeftColor = '#3498db';
    }
    updateBalance(data.balance);
}

// 3. SLOTS LOGIC
async function playSlots() {
    const betAmount = document.getElementById('slots-bet-amount').value;

    const res = await fetch('/api/slots/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bet_amount: betAmount })
    });

    const data = await res.json();
    if (res.status !== 200) return alert(data.error);

    document.getElementById('reel1').innerText = data.reels[0];
    document.getElementById('reel2').innerText = data.reels[1];
    document.getElementById('reel3').innerText = data.reels[2];

    const status = document.getElementById('slots-status');
    if (data.win) {
        status.innerHTML = `🎰 JACKPOT / WIN! (${data.multiplier}배당) | 획득: +$${data.net_change.toLocaleString()}`;
        status.style.borderLeftColor = '#2ecc71';
    } else {
        status.innerHTML = `❌ 아쉽네요! 다시 도전하세요. | 손실: -$${Math.abs(data.net_change).toLocaleString()}`;
        status.style.borderLeftColor = '#e74c3c';
    }
    updateBalance(data.balance);
}

// 4. DREAM CATCHER LOGIC
async function playDreamCatcher(target) {
    const betAmount = document.getElementById('dream-bet-amount').value;

    const res = await fetch('/api/dreamcatcher/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target, bet_amount: betAmount })
    });

    const data = await res.json();
    if (res.status !== 200) return alert(data.error);

    document.getElementById('wheel-target-result').innerText = data.hit_segment;

    const status = document.getElementById('dream-status');
    if (data.win) {
        status.innerHTML = `🎯 당첨! 정지 위치: <strong>${data.hit_segment}</strong> (${data.multiplier}배) | 획득: +$${data.net_change.toLocaleString()}`;
        status.style.borderLeftColor = '#2ecc71';
    } else {
        status.innerHTML = `❌ 낙첨... 정지 위치: <strong>${data.hit_segment}</strong> | 손실: -$${Math.abs(data.net_change).toLocaleString()}`;
        status.style.borderLeftColor = '#e74c3c';
    }
    updateBalance(data.balance);
}

// 5. SIC BO LOGIC
async function playSicBo(betType, betValue) {
    const betAmount = document.getElementById('sicbo-bet-amount').value;

    const res = await fetch('/api/sicbo/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bet_type: betType, bet_value: betValue, bet_amount: betAmount })
    });

    const data = await res.json();
    if (res.status !== 200) return alert(data.error);

    document.getElementById('sicbo-d1').innerText = data.dice[0];
    document.getElementById('sicbo-d2').innerText = data.dice[1];
    document.getElementById('sicbo-d3').innerText = data.dice[2];
    document.getElementById('sicbo-sum-val').innerText = data.dice_sum;

    const status = document.getElementById('sicbo-status');
    if (data.win) {
        status.innerHTML = `🎉 당첨! 주사위 결과: [${data.dice.join(', ')}] (합: ${data.dice_sum}) | 획득: +$${data.net_change.toLocaleString()}`;
        status.style.borderLeftColor = '#2ecc71';
    } else {
        status.innerHTML = `❌ 낙첨... 주사위 결과: [${data.dice.join(', ')}] (합: ${data.dice_sum}) | 손실: -$${Math.abs(data.net_change).toLocaleString()}`;
        status.style.borderLeftColor = '#e74c3c';
    }
    updateBalance(data.balance);
}
