import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="2인용 탑다운 슈팅 게임",
    layout="wide"
)

st.title("🎮 2인용 1대1 탑다운 슈팅 게임")

st.write("""
**P1**: WASD 이동 / IJKL 조준 / F 발사  
**P2**: 방향키 이동 / 숫자패드 8·4·5·6 조준 / Enter 발사  
먼저 맵의 무기를 획득하고 상대 HP를 0으로 만들면 승리!
""")

game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        overflow: hidden;
        background: #222;
        font-family: Arial, sans-serif;
    }

    canvas {
        display: block;
        margin: auto;
        background: #4f913f;
        border: 4px solid #111;
    }
</style>
</head>

<body>

<canvas id="gameCanvas" width="1200" height="750"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

const WORLD_W = 2400;
const WORLD_H = 1600;

const keys = {};

window.addEventListener("keydown", function(e) {
    keys[e.key] = true;

    const blockedKeys = [
        "ArrowUp", "ArrowDown",
        "ArrowLeft", "ArrowRight",
        " "
    ];

    if (blockedKeys.includes(e.key)) {
        e.preventDefault();
    }

    if (!gameOver) {
        if (e.key === "f" || e.key === "F") {
            shoot(p1);
        }

        if (e.key === "Enter") {
            shoot(p2);
        }
    }

    if (gameOver && (e.key === "r" || e.key === "R")) {
        restartGame();
    }
});

window.addEventListener("keyup", function(e) {
    keys[e.key] = false;
});


/* =========================
   플레이어
========================= */

function createPlayer(x, y, color, name) {
    return {
        x: x,
        y: y,
        color: color,
        name: name,

        radius: 24,
        speed: 4.5,

        hp: 100,
        hasWeapon: false,

        aimX: 1,
        aimY: 0,

        shootTimer: 0
    };
}

let p1 = createPlayer(
    150,
    150,
    "#f5d52a",
    "P1"
);

let p2 = createPlayer(
    2200,
    1400,
    "#3d8cff",
    "P2"
);


/* =========================
   구조물
========================= */

const obstacles = [];

function addObstacle(x, y, w, h, type) {
    obstacles.push({
        x, y, w, h, type
    });
}


/* ===== 집 ===== */

addObstacle(250, 180, 400, 35, "wall");
addObstacle(250, 180, 35, 300, "wall");
addObstacle(615, 180, 35, 300, "wall");

addObstacle(250, 445, 150, 35, "wall");
addObstacle(500, 445, 150, 35, "wall");

addObstacle(340, 260, 110, 55, "crate");
addObstacle(500, 330, 70, 70, "crate");


/* ===== 창고 ===== */

addObstacle(1550, 950, 500, 40, "wall");
addObstacle(1550, 950, 40, 350, "wall");
addObstacle(2010, 950, 40, 350, "wall");

addObstacle(1550, 1260, 190, 40, "wall");
addObstacle(1850, 1260, 200, 40, "wall");

addObstacle(1650, 1040, 90, 90, "crate");
addObstacle(1850, 1080, 120, 70, "crate");
addObstacle(1720, 1180, 80, 60, "crate");


/* ===== 콘크리트 엄폐물 ===== */

addObstacle(900, 600, 350, 45, "concrete");
addObstacle(900, 600, 45, 200, "concrete");

addObstacle(1200, 350, 300, 45, "concrete");
addObstacle(1455, 350, 45, 200, "concrete");

addObstacle(650, 1050, 45, 250, "concrete");
addObstacle(650, 1255, 250, 45, "concrete");


/* ===== 자동차 ===== */

addObstacle(1100, 820, 170, 80, "car");
addObstacle(1350, 820, 170, 80, "car");


/* ===== 나무 ===== */

const trees = [
    [100, 800],
    [170, 850],
    [240, 780],

    [2150, 300],
    [2250, 360],
    [2300, 260],

    [350, 1300],
    [450, 1350],
    [520, 1280]
];

for (const t of trees) {
    addObstacle(t[0], t[1], 70, 70, "tree");
}


/* ===== 바위 ===== */

const rocks = [
    [750, 300],
    [820, 340],
    [1950, 500],
    [2050, 550],
    [300, 1050]
];

for (const r of rocks) {
    addObstacle(r[0], r[1], 80, 60, "rock");
}


/* ===== 드럼통 ===== */

const drums = [
    [500, 900],
    [570, 900],
    [640, 900],

    [2100, 1200],
    [2160, 1200]
];

for (const d of drums) {
    addObstacle(d[0], d[1], 40, 40, "drum");
}


/* =========================
   무기
========================= */

let weapons = [
    {x: 800, y: 850, taken: false},
    {x: 1200, y: 500, taken: false},
    {x: 1700, y: 700, taken: false}
];


/* =========================
   총알
========================= */

let bullets = [];


/* =========================
   게임 상태
========================= */

let gameOver = false;
let winner = "";


/* =========================
   충돌 검사
========================= */

function playerHitsObstacle(player, x, y) {

    const left = x - player.radius;
    const right = x + player.radius;
    const top = y - player.radius;
    const bottom = y + player.radius;

    for (const o of obstacles) {

        if (
            right > o.x &&
            left < o.x + o.w &&
            bottom > o.y &&
            top < o.y + o.h
        ) {
            return true;
        }
    }

    return false;
}


/* =========================
   플레이어 이동
========================= */

function updatePlayer(player, controls) {

    let dx = 0;
    let dy = 0;

    if (keys[controls.up]) dy--;
    if (keys[controls.down]) dy++;
    if (keys[controls.left]) dx--;
    if (keys[controls.right]) dx++;

    if (dx !== 0 || dy !== 0) {

        const length = Math.sqrt(dx * dx + dy * dy);

        dx /= length;
        dy /= length;

        const newX = player.x + dx * player.speed;
        const newY = player.y + dy * player.speed;

        if (!playerHitsObstacle(player, newX, player.y)) {
            player.x = newX;
        }

        if (!playerHitsObstacle(player, player.x, newY)) {
            player.y = newY;
        }
    }


    /* 맵 경계 */

    player.x = Math.max(
        player.radius,
        Math.min(WORLD_W - player.radius, player.x)
    );

    player.y = Math.max(
        player.radius,
        Math.min(WORLD_H - player.radius, player.y)
    );


    /* 조준 */

    let ax = 0;
    let ay = 0;

    if (keys[controls.aimUp]) ay--;
    if (keys[controls.aimDown]) ay++;
    if (keys[controls.aimLeft]) ax--;
    if (keys[controls.aimRight]) ax++;

    if (ax !== 0 || ay !== 0) {

        const len = Math.sqrt(ax * ax + ay * ay);

        player.aimX = ax / len;
        player.aimY = ay / len;
    }

    if (player.shootTimer > 0) {
        player.shootTimer--;
    }
}


/* =========================
   총 발사
========================= */

function shoot(player) {

    if (!player.hasWeapon) return;

    if (player.shootTimer > 0) return;

    player.shootTimer = 15;

    bullets.push({
        x: player.x + player.aimX * 40,
        y: player.y + player.aimY * 40,

        dx: player.aimX,
        dy: player.aimY,

        owner: player,

        speed: 12,
        damage: 15,
        radius: 6
    });
}


/* =========================
   총알 업데이트
========================= */

function updateBullets() {

    for (let i = bullets.length - 1; i >= 0; i--) {

        const b = bullets[i];

        b.x += b.dx * b.speed;
        b.y += b.dy * b.speed;

        let remove = false;


        /* 구조물 충돌 */

        for (const o of obstacles) {

            if (
                b.x > o.x &&
                b.x < o.x + o.w &&
                b.y > o.y &&
                b.y < o.y + o.h
            ) {
                remove = true;
            }
        }


        /* 플레이어 충돌 */

        for (const p of [p1, p2]) {

            if (p !== b.owner) {

                const dx = b.x - p.x;
                const dy = b.y - p.y;

                const distance =
                    Math.sqrt(dx * dx + dy * dy);

                if (distance < p.radius + b.radius) {

                    p.hp -= b.damage;
                    remove = true;

                    if (p.hp <= 0) {

                        p.hp = 0;
                        gameOver = true;

                        winner =
                            b.owner.name + " WINS!";
                    }
                }
            }
        }


        /* 맵 밖 */

        if (
            b.x < 0 ||
            b.x > WORLD_W ||
            b.y < 0 ||
            b.y > WORLD_H
        ) {
            remove = true;
        }

        if (remove) {
            bullets.splice(i, 1);
        }
    }
}


/* =========================
   무기 획득
========================= */

function updateWeapons() {

    for (const weapon of weapons) {

        if (weapon.taken) continue;

        for (const player of [p1, p2]) {

            const dx = player.x - weapon.x;
            const dy = player.y - weapon.y;

            const distance =
                Math.sqrt(dx * dx + dy * dy);

            if (distance < 45) {

                player.hasWeapon = true;
                weapon.taken = true;
            }
        }
    }
}


/* =========================
   카메라
========================= */

function getCamera() {

    const centerX = (p1.x + p2.x) / 2;
    const centerY = (p1.y + p2.y) / 2;

    let camX = centerX - W / 2;
    let camY = centerY - H / 2;

    camX = Math.max(
        0,
        Math.min(WORLD_W - W, camX)
    );

    camY = Math.max(
        0,
        Math.min(WORLD_H - H, camY)
    );

    return {
        x: camX,
        y: camY
    };
}


/* =========================
   구조물 그리기
========================= */

function drawObstacle(o, cam) {

    const x = o.x - cam.x;
    const y = o.y - cam.y;

    if (o.type === "wall") {

        ctx.fillStyle = "#c7b69e";
        ctx.fillRect(x, y, o.w, o.h);

        ctx.strokeStyle = "#555";
        ctx.lineWidth = 4;
        ctx.strokeRect(x, y, o.w, o.h);
    }


    if (o.type === "crate") {

        ctx.fillStyle = "#8b552d";
        ctx.fillRect(x, y, o.w, o.h);

        ctx.strokeStyle = "#553015";
        ctx.lineWidth = 4;
        ctx.strokeRect(x, y, o.w, o.h);

        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + o.w, y + o.h);

        ctx.moveTo(x + o.w, y);
        ctx.lineTo(x, y + o.h);

        ctx.stroke();
    }


    if (o.type === "concrete") {

        ctx.fillStyle = "#777";
        ctx.fillRect(x, y, o.w, o.h);

        ctx.strokeStyle = "#444";
        ctx.lineWidth = 4;
        ctx.strokeRect(x, y, o.w, o.h);

        ctx.strokeStyle = "#666";

        for (let bx = x; bx < x + o.w; bx += 35) {

            ctx.beginPath();
            ctx.moveTo(bx, y);
            ctx.lineTo(bx, y + o.h);
            ctx.stroke();
        }
    }


    if (o.type === "car") {

        ctx.fillStyle = "#bd3434";
        ctx.fillRect(x, y, o.w, o.h);

        ctx.fillStyle = "#7cc6e8";
        ctx.fillRect(
            x + 35,
            y + 12,
            o.w - 70,
            25
        );

        ctx.fillStyle = "#111";

        ctx.beginPath();
        ctx.arc(x + 30, y + o.h, 13, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.arc(
            x + o.w - 30,
            y + o.h,
            13,
            0,
            Math.PI * 2
        );
        ctx.fill();
    }


    if (o.type === "tree") {

        ctx.fillStyle = "#613b1c";

        ctx.beginPath();
        ctx.arc(
            x + o.w / 2,
            y + o.h / 2,
            14,
            0,
            Math.PI * 2
        );
        ctx.fill();

        ctx.fillStyle = "#2e7d32";

        ctx.beginPath();
        ctx.arc(
            x + o.w / 2,
            y + o.h / 2,
            34,
            0,
            Math.PI * 2
        );
        ctx.fill();

        ctx.fillStyle = "#48a848";

        ctx.beginPath();
        ctx.arc(
            x + o.w / 2 - 10,
            y + o.h / 2 - 10,
            20,
            0,
            Math.PI * 2
        );
        ctx.fill();
    }


    if (o.type === "rock") {

        ctx.fillStyle = "#888";

        ctx.beginPath();
        ctx.ellipse(
            x + o.w / 2,
            y + o.h / 2,
            o.w / 2,
            o.h / 2,
            0,
            0,
            Math.PI * 2
        );

        ctx.fill();

        ctx.strokeStyle = "#555";
        ctx.stroke();
    }


    if (o.type === "drum") {

        ctx.fillStyle = "#287ac2";
        ctx.fillRect(x, y, o.w, o.h);

        ctx.strokeStyle = "white";

        ctx.beginPath();
        ctx.moveTo(x, y + 12);
        ctx.lineTo(x + o.w, y + 12);

        ctx.moveTo(x, y + o.h - 12);
        ctx.lineTo(x + o.w, y + o.h - 12);

        ctx.stroke();
    }
}


/* =========================
   플레이어 그리기
========================= */

function drawPlayer(p, cam) {

    const x = p.x - cam.x;
    const y = p.y - cam.y;


    /* 그림자 */

    ctx.fillStyle = "rgba(0,0,0,0.25)";

    ctx.beginPath();

    ctx.ellipse(
        x,
        y + 15,
        22,
        10,
        0,
        0,
        Math.PI * 2
    );

    ctx.fill();


    /* 몸 */

    ctx.fillStyle = p.color;

    ctx.beginPath();
    ctx.arc(x, y + 4, 22, 0, Math.PI * 2);
    ctx.fill();


    /* 머리 */

    ctx.fillStyle = "#f0c99b";

    ctx.beginPath();
    ctx.arc(x, y - 15, 13, 0, Math.PI * 2);
    ctx.fill();


    /* 팔 + 총 */

    ctx.strokeStyle = "#f0c99b";
    ctx.lineWidth = 10;

    ctx.beginPath();

    ctx.moveTo(x, y);

    ctx.lineTo(
        x + p.aimX * 22,
        y + p.aimY * 22
    );

    ctx.stroke();


    if (p.hasWeapon) {

        ctx.strokeStyle = "#222";
        ctx.lineWidth = 8;

        ctx.beginPath();

        ctx.moveTo(
            x + p.aimX * 15,
            y + p.aimY * 15
        );

        ctx.lineTo(
            x + p.aimX * 48,
            y + p.aimY * 48
        );

        ctx.stroke();
    }


    /* HP 바 */

    ctx.fillStyle = "#d33";

    ctx.fillRect(
        x - 32,
        y - 52,
        64,
        8
    );

    ctx.fillStyle = "#39d353";

    ctx.fillRect(
        x - 32,
        y - 52,
        64 * (p.hp / 100),
        8
    );


    /* 이름 */

    ctx.fillStyle = "white";
    ctx.font = "18px Arial";
    ctx.textAlign = "center";

    ctx.fillText(
        p.name,
        x,
        y - 62
    );
}


/* =========================
   무기 그리기
========================= */

function drawWeapons(cam) {

    for (const w of weapons) {

        if (w.taken) continue;

        const x = w.x - cam.x;
        const y = w.y - cam.y;

        ctx.fillStyle = "#f5c542";

        ctx.beginPath();
        ctx.arc(x, y, 25, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#111";

        ctx.fillRect(
            x - 8,
            y - 10,
            35,
            10
        );

        ctx.fillRect(
            x + 15,
            y - 5,
            12,
            20
        );
    }
}


/* =========================
   총알 그리기
========================= */

function drawBullets(cam) {

    for (const b of bullets) {

        ctx.fillStyle = "#ff9d00";

        ctx.beginPath();

        ctx.arc(
            b.x - cam.x,
            b.y - cam.y,
            b.radius,
            0,
            Math.PI * 2
        );

        ctx.fill();
    }
}


/* =========================
   UI
========================= */

function drawUI() {

    ctx.fillStyle = "rgba(0,0,0,0.6)";
    ctx.fillRect(0, 0, W, 55);

    ctx.fillStyle = "white";
    ctx.font = "20px Arial";
    ctx.textAlign = "left";

    ctx.fillText(
        "P1 HP: " + p1.hp +
        (p1.hasWeapon ? "  🔫" : "  맨손"),
        20,
        35
    );

    ctx.textAlign = "right";

    ctx.fillText(
        "P2 HP: " + p2.hp +
        (p2.hasWeapon ? "  🔫" : "  맨손"),
        W - 20,
        35
    );

    ctx.font = "15px Arial";
    ctx.textAlign = "center";

    ctx.fillText(
        "P1: WASD 이동 / IJKL 조준 / F 발사     |     P2: 방향키 이동 / 숫자패드 8456 조준 / Enter 발사",
        W / 2,
        H - 20
    );
}


/* =========================
   게임 종료
========================= */

function drawGameOver() {

    if (!gameOver) return;

    ctx.fillStyle = "rgba(0,0,0,0.7)";
    ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = "white";
    ctx.textAlign = "center";

    ctx.font = "60px Arial";

    ctx.fillText(
        winner,
        W / 2,
        H / 2 - 30
    );

    ctx.font = "28px Arial";

    ctx.fillText(
        "R 키를 눌러 다시 시작",
        W / 2,
        H / 2 + 40
    );
}


/* =========================
   게임 재시작
========================= */

function restartGame() {

    p1 = createPlayer(
        150,
        150,
        "#f5d52a",
        "P1"
    );

    p2 = createPlayer(
        2200,
        1400,
        "#3d8cff",
        "P2"
    );

    bullets = [];

    weapons = [
        {x: 800, y: 850, taken: false},
        {x: 1200, y: 500, taken: false},
        {x: 1700, y: 700, taken: false}
    ];

    gameOver = false;
    winner = "";
}


/* =========================
   메인 게임 루프
========================= */

function gameLoop() {

    if (!gameOver) {

        updatePlayer(p1, {
            up: "w",
            down: "s",
            left: "a",
            right: "d",

            aimUp: "i",
            aimDown: "k",
            aimLeft: "j",
            aimRight: "l"
        });


        updatePlayer(p2, {
            up: "ArrowUp",
            down: "ArrowDown",
            left: "ArrowLeft",
            right: "ArrowRight",

            aimUp: "8",
            aimDown: "5",
            aimLeft: "4",
            aimRight: "6"
        });


        updateWeapons();
        updateBullets();
    }


    const cam = getCamera();


    /* 배경 */

    ctx.fillStyle = "#4f913f";
    ctx.fillRect(0, 0, W, H);


    /* 도로 */

    const roadY = 760 - cam.y;

    ctx.fillStyle = "#606060";

    ctx.fillRect(
        0,
        roadY,
        W,
        180
    );


    /* 도로 중앙선 */

    ctx.fillStyle = "#e5e0b5";

    for (
        let x = -cam.x % 80;
        x < W;
        x += 80
    ) {

        ctx.fillRect(
            x,
            roadY + 85,
            40,
            8
        );
    }


    /* 구조물 */

    for (const o of obstacles) {
        drawObstacle(o, cam);
    }


    drawWeapons(cam);
    drawBullets(cam);

    drawPlayer(p1, cam);
    drawPlayer(p2, cam);

    drawUI();
    drawGameOver();

    requestAnimationFrame(gameLoop);
}


gameLoop();

</script>
</body>
</html>
"""

components.html(
    game_html,
    height=780,
    scrolling=False
)
