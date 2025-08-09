let room = 'default';
let player = null; // 0 lub 1
let gameState = null;
let selectedUnit = null;
let mode = 'move'; // 'move' | 'attack'

const board = document.getElementById('board');
const ctx = board.getContext('2d');
const cell = 64;

async function api(path, options) {
    const res = await fetch(path, options);
    return await res.json();
}

async function join(asPlayer) {
    const data = await api('/api/session/join', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ room }) });
    player = asPlayer !== undefined ? asPlayer : data.player;
    await refreshState();
}

async function resetGame() {
    await api('/api/game/reset', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ room }) });
    await refreshState();
}

async function refreshState() {
    gameState = await api(`/api/game/state?room=${room}`);
    draw();
    document.getElementById('turnInfo').textContent = `Tura gracza: ${gameState.turn} ${player !== null ? `(ty: ${player})` : ''}`;
}

function draw() {
    if (!gameState) return;
    const map = gameState.map;
    board.width = map.width * cell;
    board.height = map.height * cell;
    // tło
    ctx.fillStyle = '#eef';
    ctx.fillRect(0, 0, board.width, board.height);
    // kratownica
    ctx.strokeStyle = '#aaa';
    for (let x = 0; x <= map.width; x++) {
        ctx.beginPath();
        ctx.moveTo(x * cell, 0);
        ctx.lineTo(x * cell, board.height);
        ctx.stroke();
    }
    for (let y = 0; y <= map.height; y++) {
        ctx.beginPath();
        ctx.moveTo(0, y * cell);
        ctx.lineTo(board.width, y * cell);
        ctx.stroke();
    }
    // teren
    for (const t of map.terrain || []) {
        const x = t.x * cell;
        const y = t.y * cell;
        ctx.fillStyle = t.type === 'forest' ? '#6a4' : '#b96';
        ctx.fillRect(x, y, cell, cell);
    }
    // jednostki
    for (const u of gameState.placements) {
        const x = u.x * cell + cell/2;
        const y = u.y * cell + cell/2;
        ctx.beginPath();
        ctx.fillStyle = u.owner === 0 ? '#0077ff' : '#ff3333';
        ctx.arc(x, y, cell*0.35, 0, Math.PI*2);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${u.type.substring(0,1).toUpperCase()}${u.hp}`, x, y+4);
        if (selectedUnit && selectedUnit.id === u.id) {
            ctx.strokeStyle = '#ff0';
            ctx.lineWidth = 3;
            ctx.strokeRect(u.x * cell + 2, u.y * cell + 2, cell - 4, cell - 4);
        }
    }
}

board.addEventListener('click', async (e) => {
    const rect = board.getBoundingClientRect();
    const gx = Math.floor((e.clientX - rect.left) / cell);
    const gy = Math.floor((e.clientY - rect.top) / cell);
    const units = gameState?.placements || [];
    const clicked = units.find(u => u.x === gx && u.y === gy);
    if (!selectedUnit) {
        if (clicked && clicked.owner === player) {
            selectedUnit = clicked;
            draw();
        }
        return;
    }

    if (mode === 'move') {
        const res = await api('/api/game/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ room, player, action: 'move', id: selectedUnit.id, to: { x: gx, y: gy } })
        });
        if (!res.error) {
            selectedUnit = null;
            await refreshState();
        } else {
            alert(res.error);
        }
    } else if (mode === 'attack') {
        if (!clicked || clicked.owner === player) return;
        const res = await api('/api/game/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ room, player, action: 'attack', id: selectedUnit.id, targetId: clicked.id })
        });
        if (!res.error) {
            selectedUnit = null;
            await refreshState();
        } else {
            alert(res.error);
        }
    }
});

document.getElementById('joinA').addEventListener('click', () => join(0));
document.getElementById('joinB').addEventListener('click', () => join(1));
document.getElementById('reset').addEventListener('click', resetGame);
document.getElementById('modeMove').addEventListener('click', () => { mode = 'move'; document.getElementById('modeMove').classList.add('active'); document.getElementById('modeAttack').classList.remove('active'); });
document.getElementById('modeAttack').addEventListener('click', () => { mode = 'attack'; document.getElementById('modeAttack').classList.add('active'); document.getElementById('modeMove').classList.remove('active'); });

refreshState();
