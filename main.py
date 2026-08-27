import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="2인용 1대1 슈팅 게임", layout="wide")

st.title("🎮 2인용 1대1 탑다운 슈팅 게임")

st.info(
    "게임 화면을 먼저 한 번 클릭한 뒤 플레이하세요! "
    "P1: WASD 이동 / IJKL 조준 / F 발사 | "
    "P2: 방향키 이동 / 8456 조준 / Enter 발사"
)

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
html, body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #202020;
}

#gameCanvas {
    display: block;
    margin: 0 auto;
    background: #4f913f;
    border: 4px solid #111;
    outline: none;
}
</style>
</head>

<body>

<canvas
    id="gameCanvas"
    width="1200"
    height="760"
    tabindex="0">
</canvas>

<script>

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const SCREEN_W = canvas.width;
const SCREEN_H = canvas.height;

const WORLD_W = 3000;
const WORLD_H = 2200;

let keys = {};

canvas.focus();


/* =====================================
   키 입력
===================================== */

window.addEventListener("keydown", (event) => {

    const blocked = [
        "ArrowUp",
        "ArrowDown",
        "ArrowLeft",
        "ArrowRight",
        " ",
        "Enter"
    ];

    if (blocked.includes(event.key)) {
        event.preventDefault();
    }

    keys[event.key] = true;

    if (!gameOver) {

        if (event.key === "f" || event.key === "F") {
            shoot(p1);
        }

        if (event.key === "Enter") {
            shoot(p2);
        }
    }

    if (
        gameOver &&
        (event.key === "r" || event.key === "R")
    ) {
        restartGame();
    }
});


window.addEventListener("keyup", (event) => {

    keys[event.key] = false;

});


canvas.addEventListener("click", () => {
    canvas.focus();
});


/* =====================================
   플레이어 생성
===================================== */

function createPlayer(x, y, color, name) {

    return {

        x: x,
        y: y,

        color: color,
        name: name,

        radius: 24,

        speed: 5,

        hp: 100,

        hasWeapon: false,

        aimX: 1,
        aimY: 0,

        cooldown: 0

    };

}


let p1 = createPlayer(
    300,
    300,
    "#f4d03f",
    "P1"
);


let p2 = createPlayer(
    2700,
    1900,
    "#3498db",
    "P2"
);


/* =====================================
   구조물
===================================== */

const obstacles = [];

function addObstacle(x, y, w, h, type) {

    obstacles.push({
        x: x,
        y: y,
        w: w,
        h: h,
        type: type
    });

}


/* ===== P1 주변 집 ===== */

addObstacle(400, 200, 500, 40, "houseWall");
addObstacle(400, 200, 40, 350, "houseWall");
addObstacle(860, 200, 40, 350, "houseWall");

addObstacle(400, 510, 180, 40, "houseWall");
addObstacle(700, 510, 200, 40, "houseWall");

addObstacle(520, 300, 100, 60, "crate");
addObstacle(700, 350, 100, 100, "crate");


/* ===== 중앙 엄폐물 ===== */

addObstacle(1200, 500, 400, 50, "concrete");
addObstacle(1200, 500, 50, 250, "concrete");

addObstacle(1700, 700, 400, 50, "concrete");
addObstacle(2050, 700, 50, 250, "concrete");

addObstacle(900, 1100, 50, 300, "concrete");
addObstacle(900, 1350, 350, 50, "concrete");


/* ===== 중앙 자동차 ===== */

addObstacle(1300, 900, 190, 85, "car");
addObstacle(1600, 900, 190, 85, "car");


/* ===== P2 주변 창고 ===== */

addObstacle(2200, 1500, 500, 45, "houseWall");
addObstacle(2200, 1500, 45, 400, "houseWall");
addObstacle(2655, 1500, 45, 400, "houseWall");

addObstacle(2200, 1855, 180, 45, "houseWall");
addObstacle(2500, 1855, 200, 45, "houseWall");

addObstacle(2320, 1620, 120, 100, "crate");
addObstacle(2500, 1700, 120, 80, "crate");


/* ===== 나무 ===== */

const trees = [

    [100, 800],
    [200, 850],
    [300, 900],
    [150, 1000],

    [500, 1600],
    [600, 1650],
    [700, 1700],

    [2500, 300],
    [2650, 350],
    [2800, 250],

    [2700, 1100],
    [2800, 1200]

];

for (const t of trees) {

    addObstacle(
        t[0],
        t[1],
        75,
        75,
        "tree"
    );

}


/* ===== 바위 ===== */

const rocks = [

    [700, 700],
    [800, 750],
    [1900, 350],
    [2000, 400],
    [500, 1300],
    [1500, 1500]

];

for (const r of rocks) {

    addObstacle(
        r[0],
        r[1],
        85,
        65,
        "rock"
    );

}


/* ===== 드럼통 ===== */

const drums = [

    [1050, 900],
    [1100, 900],
    [1150, 900],

    [2000, 1300],
    [2050, 1300]

];

for (const d of drums) {

    addObstacle(
        d[0],
        d[1],
        40,
        40,
        "drum"
    );

}


/* =====================================
   무기
===================================== */

let weapons = [

    {
        x: 1050,
        y: 800,
        taken: false
    },

    {
        x: 1500,
        y: 700,
        taken: false
    },

    {
        x: 1900,
        y: 1200,
        taken: false
    }

];


/* =====================================
   총알
===================================== */

let bullets = [];


/* =====================================
   게임 상태
===================================== */

let gameOver = false;
let winner = "";


/* =====================================
   충돌 검사
===================================== */

function hitsObstacle(player, x, y) {

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


/* =====================================
   플레이어 이동
===================================== */

function updatePlayer(player, control) {

    let dx = 0;
    let dy = 0;


    /* 이동 */

    if (keys[control.up]) dy -= 1;
    if (keys[control.down]) dy += 1;

    if (keys[control.left]) dx -= 1;
    if (keys[control.right]) dx += 1;


    if (dx !== 0 || dy !== 0) {

        const length = Math.sqrt(
            dx * dx + dy * dy
        );

        dx /= length;
        dy /= length;

        const newX =
            player.x + dx * player.speed;

        const newY =
            player.y + dy * player.speed;


        /* X축 이동 */

        if (
            !hitsObstacle(
                player,
                newX,
                player.y
            )
        ) {

            player.x = newX;

        }


        /* Y축 이동 */

        if (
            !hitsObstacle(
                player,
                player.x,
                newY
            )
        ) {

            player.y = newY;

        }

    }


    /* 맵 경계 */

    player.x = Math.max(
        player.radius,
        Math.min(
            WORLD_W - player.radius,
            player.x
        )
    );

    player.y = Math.max(
        player.radius,
        Math.min(
            WORLD_H - player.radius,
            player.y
        )
    );


    /* 조준 */

    let aimX = 0;
    let aimY = 0;


    if (keys[control.aimUp]) aimY -= 1;
    if (keys[control.aimDown]) aimY += 1;

    if (keys[control.aimLeft]) aimX -= 1;
    if (keys[control.aimRight]) aimX += 1;


    if (aimX !== 0 || aimY !== 0) {

        const length = Math.sqrt(
            aimX * aimX +
            aimY * aimY
        );

        player.aimX = aimX / length;
        player.aimY = aimY / length;

    }


    if (player.cooldown > 0) {
        player.cooldown--;
    }

}


/* =====================================
   총 발사
===================================== */

function shoot(player) {

    if (!player.hasWeapon) {
        return;
    }

    if (player.cooldown > 0) {
        return;
    }


    player.cooldown = 18;


    bullets.push({

        x:
            player.x +
            player.aimX * 45,

        y:
            player.y +
            player.aimY * 45,

        dx: player.aimX,
        dy: player.aimY,

        owner: player,

        speed: 13,

        radius: 6,

        damage: 15

    });

}


/* =====================================
   총알 업데이트
===================================== */

function updateBullets() {

    for (
        let i = bullets.length - 1;
        i >= 0;
        i--
    ) {

        const bullet = bullets[i];


        bullet.x +=
            bullet.dx * bullet.speed;

        bullet.y +=
            bullet.dy * bullet.speed;


        let remove = false;


        /* 구조물 */

        for (const o of obstacles) {

            if (

                bullet.x > o.x &&
                bullet.x < o.x + o.w &&

                bullet.y > o.y &&
                bullet.y < o.y + o.h

            ) {

                remove = true;

            }

        }


        /* 플레이어 */

        for (const player of [p1, p2]) {

            if (
                player === bullet.owner
            ) continue;


            const dx =
                bullet.x - player.x;

            const dy =
                bullet.y - player.y;


            const distance =
                Math.sqrt(
                    dx * dx +
                    dy * dy
                );


            if (
                distance <
                player.radius +
                bullet.radius
            ) {

                player.hp -=
                    bullet.damage;

                remove = true;


                if (
                    player.hp <= 0
                ) {

                    player.hp = 0;

                    gameOver = true;

                    winner =
                        bullet.owner.name +
                        " 승리!";

                }

            }

        }


        /* 맵 밖 */

        if (

            bullet.x < 0 ||
            bullet.x > WORLD_W ||

            bullet.y < 0 ||
            bullet.y > WORLD_H

        ) {

            remove = true;

        }


        if (remove) {

            bullets.splice(i, 1);

        }

    }

}


/* =====================================
   무기 획득
===================================== */

function updateWeapons() {

    for (const weapon of weapons) {

        if (weapon.taken) continue;


        for (
            const player of [p1, p2]
        ) {

            const dx =
                player.x - weapon.x;

            const dy =
                player.y - weapon.y;


            const distance =
                Math.sqrt(
                    dx * dx +
                    dy * dy
                );


            if (distance < 50) {

                player.hasWeapon = true;
                weapon.taken = true;

            }

        }

    }

}


/* =====================================
   카메라
   두 캐릭터의 중간을 따라감
===================================== */

function getCamera() {

    const centerX =
        (p1.x + p2.x) / 2;

    const centerY =
        (p1.y + p2.y) / 2;


    let x =
        centerX - SCREEN_W / 2;

    let y =
        centerY - SCREEN_H / 2;


    x = Math.max(
        0,
        Math.min(
            WORLD_W - SCREEN_W,
            x
        )
    );


    y = Math.max(
        0,
        Math.min(
            WORLD_H - SCREEN_H,
            y
        )
    );


    return {
        x: x,
        y: y
    };

}


/* =====================================
   구조물 그리기
===================================== */

function drawObstacle(o, cam) {

    const x = o.x - cam.x;
    const y = o.y - cam.y;


    if (
        x > SCREEN_W ||
        y > SCREEN_H ||
        x + o.w < 0 ||
        y + o.h < 0
    ) return;


    if (o.type === "houseWall") {

        ctx.fillStyle = "#c9b18f";
        ctx.fillRect(x, y, o.w, o.h);

        ctx.strokeStyle = "#594d40";
        ctx.lineWidth = 4;
        ctx.strokeRect(x, y, o.w, o.h);

    }


    else if (o.type === "crate") {

        ctx.fillStyle = "#985a2b";
        ctx.fillRect(x, y, o.w, o.h);

        ctx.strokeStyle = "#5c3215";
        ctx.lineWidth = 4;
        ctx.strokeRect(x, y, o.w, o.h);

        ctx.beginPath();

        ctx.moveTo(x, y);
        ctx.lineTo(
            x + o.w,
            y + o.h
        );

        ctx.moveTo(
            x + o.w,
            y
        );

        ctx.lineTo(
            x,
            y + o.h
        );

        ctx.stroke();

    }


    else if (o.type === "concrete") {

        ctx.fillStyle = "#858585";
        ctx.fillRect(x, y, o.w, o.h);

        ctx.strokeStyle = "#444";
        ctx.lineWidth = 4;
        ctx.strokeRect(x, y, o.w, o.h);


        ctx.strokeStyle = "#666";


        for (
            let bx = x;
            bx < x + o.w;
            bx += 40
        ) {

            ctx.beginPath();

            ctx.moveTo(bx, y);
            ctx.lineTo(
                bx,
                y + o.h
            );

            ctx.stroke();

        }

    }


    else if (o.type === "car") {

        ctx.fillStyle = "#b52e2e";

        ctx.fillRect(
            x,
            y,
            o.w,
            o.h
        );


        ctx.fillStyle = "#75c5e8";

        ctx.fillRect(
            x + 35,
            y + 12,
            o.w - 70,
            28
        );


        ctx.fillStyle = "#111";


        ctx.beginPath();

        ctx.arc(
            x + 30,
            y + o.h,
            14,
            0,
            Math.PI * 2
        );

        ctx.fill();


        ctx.beginPath();

        ctx.arc(
            x + o.w - 30,
            y + o.h,
            14,
            0,
            Math.PI * 2
        );

        ctx.fill();

    }


    else if (o.type === "tree") {

        ctx.fillStyle = "#623b1e";

        ctx.beginPath();

        ctx.arc(
            x + o.w / 2,
            y + o.h / 2,
            16,
            0,
            Math.PI * 2
        );

        ctx.fill();


        ctx.fillStyle = "#287a35";

        ctx.beginPath();

        ctx.arc(
            x + o.w / 2,
            y + o.h / 2,
            37,
            0,
            Math.PI * 2
        );

        ctx.fill();


        ctx.fillStyle = "#48a84e";

        ctx.beginPath();

        ctx.arc(
            x + o.w / 2 - 10,
            y + o.h / 2 - 10,
            22,
            0,
            Math.PI * 2
        );

        ctx.fill();

    }


    else if (o.type === "rock") {

        ctx.fillStyle = "#85898d";

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
        ctx.lineWidth = 3;
        ctx.stroke();

    }


    else if (o.type === "drum") {

        ctx.fillStyle = "#287fc7";
        ctx.fillRect(x, y, o.w, o.h);


        ctx.strokeStyle = "#dcefff";
        ctx.lineWidth = 3;


        ctx.beginPath();

        ctx.moveTo(
            x,
            y + 12
        );

        ctx.lineTo(
            x + o.w,
            y + 12
        );

        ctx.moveTo(
            x,
            y + o.h - 12
        );

        ctx.lineTo(
            x + o.w,
            y + o.h - 12
        );

        ctx.stroke();

    }

}


/* =====================================
   캐릭터 그리기
===================================== */

function drawPlayer(player, cam) {

    const x =
        player.x - cam.x;

    const y =
        player.y - cam.y;


    /* 그림자 */

    ctx.fillStyle =
        "rgba(0,0,0,0.25)";

    ctx.beginPath();

    ctx.ellipse(
        x,
        y + 15,
        24,
        10,
        0,
        0,
        Math.PI * 2
    );

    ctx.fill();


    /* 다리 */

    ctx.fillStyle = "#333";

    ctx.beginPath();

    ctx.arc(
        x - 11,
        y + 15,
        10,
        0,
        Math.PI * 2
    );

    ctx.fill();


    ctx.beginPath();

    ctx.arc(
        x + 11,
        y + 15,
        10,
        0,
        Math.PI * 2
    );

    ctx.fill();


    /* 몸통 */

    ctx.fillStyle =
        player.color;

    ctx.beginPath();

    ctx.arc(
        x,
        y + 3,
        23,
        0,
        Math.PI * 2
    );

    ctx.fill();


    /* 머리 */

    ctx.fillStyle = "#f1c99e";

    ctx.beginPath();

    ctx.arc(
        x,
        y - 16,
        13,
        0,
        Math.PI * 2
    );

    ctx.fill();


    /* 팔 */

    ctx.strokeStyle = "#f1c99e";
    ctx.lineWidth = 10;

    ctx.beginPath();

    ctx.moveTo(
        x,
        y
    );

    ctx.lineTo(
        x +
        player.aimX * 24,

        y +
        player.aimY * 24
    );

    ctx.stroke();


    /* 총 */

    if (player.hasWeapon) {

        ctx.strokeStyle = "#1d1d1d";
        ctx.lineWidth = 9;

        ctx.beginPath();

        ctx.moveTo(
            x +
            player.aimX * 15,

            y +
            player.aimY * 15
        );

        ctx.lineTo(
            x +
            player.aimX * 52,

            y +
            player.aimY * 52
        );

        ctx.stroke();

    }


    /* HP */

    ctx.fillStyle = "#d93232";

    ctx.fillRect(
        x - 35,
        y - 58,
        70,
        9
    );


    ctx.fillStyle = "#39d353";

    ctx.fillRect(
        x - 35,
        y - 58,
        70 *
        (player.hp / 100),
        9
    );


    /* 이름 */

    ctx.fillStyle = "white";
    ctx.font = "bold 17px Arial";
    ctx.textAlign = "center";

    ctx.fillText(
        player.name,
        x,
        y - 67
    );

}


/* =====================================
   무기 그리기
===================================== */

function drawWeapons(cam) {

    for (const weapon of weapons) {

        if (weapon.taken) continue;


        const x =
            weapon.x - cam.x;

        const y =
            weapon.y - cam.y;


        ctx.fillStyle =
            "rgba(255,215,0,0.35)";

        ctx.beginPath();

        ctx.arc(
            x,
            y,
            32,
            0,
            Math.PI * 2
        );

        ctx.fill();


        ctx.fillStyle = "#222";

        ctx.fillRect(
            x - 12,
            y - 7,
            38,
            12
        );


        ctx.fillRect(
            x + 12,
            y,
            13,
            22
        );

    }

}


/* =====================================
   총알 그리기
===================================== */

function drawBullets(cam) {

    for (const bullet of bullets) {

        ctx.fillStyle = "#ff9d00";

        ctx.beginPath();

        ctx.arc(
            bullet.x - cam.x,
            bullet.y - cam.y,
            bullet.radius,
            0,
            Math.PI * 2
        );

        ctx.fill();

    }

}


/* =====================================
   UI
===================================== */

function drawUI() {

    ctx.fillStyle =
        "rgba(0,0,0,0.65)";

    ctx.fillRect(
        0,
        0,
        SCREEN_W,
        58
    );


    ctx.font =
        "bold 20px Arial";


    ctx.textAlign = "left";

    ctx.fillStyle = "#f4d03f";

    ctx.fillText(
        "P1 HP: " + p1.hp +
        (p1.hasWeapon ? " 🔫" : ""),
        20,
        35
    );


    ctx.textAlign = "right";

    ctx.fillStyle = "#3498db";

    ctx.fillText(
        "P2 HP: " + p2.hp +
        (p2.hasWeapon ? " 🔫" : ""),
        SCREEN_W - 20,
        35
    );


    ctx.fillStyle = "white";
    ctx.font = "14px Arial";
    ctx.textAlign = "center";

    ctx.fillText(
        "P1: WASD 이동 / IJKL 조준 / F 발사     |     P2: 방향키 이동 / 8456 조준 / Enter 발사",
        SCREEN_W / 2,
        SCREEN_H - 20
    );

}


/* =====================================
   게임 종료
===================================== */

function drawGameOver() {

    if (!gameOver) return;


    ctx.fillStyle =
        "rgba(0,0,0,0.72)";

    ctx.fillRect(
        0,
        0,
        SCREEN_W,
        SCREEN_H
    );


    ctx.fillStyle = "white";
    ctx.textAlign = "center";

    ctx.font =
        "bold 64px Arial";

    ctx.fillText(
        winner,
        SCREEN_W / 2,
        SCREEN_H / 2 - 20
    );


    ctx.font =
        "28px Arial";

    ctx.fillText(
        "R 키를 눌러 다시 시작",
        SCREEN_W / 2,
        SCREEN_H / 2 + 45
    );

}


/* =====================================
   재시작
===================================== */

function restartGame() {

    p1 = createPlayer(
        300,
        300,
        "#f4d03f",
        "P1"
    );


    p2 = createPlayer(
        2700,
        1900,
        "#3498db",
        "P2"
    );


    bullets = [];


    weapons = [

        {
            x: 1050,
            y: 800,
            taken: false
        },

        {
            x: 1500,
            y: 700,
            taken: false
        },

        {
            x: 1900,
            y: 1200,
            taken: false
        }

    ];


    gameOver = false;
    winner = "";

}


/* =====================================
   게임 루프
===================================== */

function gameLoop() {

    if (!gameOver) {

        /* P1 */

        updatePlayer(
            p1,
            {
                up: "w",
                down: "s",
                left: "a",
                right: "d",

                aimUp: "i",
                aimDown: "k",
                aimLeft: "j",
                aimRight: "l"
            }
        );


        /* P2 */

        updatePlayer(
            p2,
            {
                up: "ArrowUp",
                down: "ArrowDown",
                left: "ArrowLeft",
                right: "ArrowRight",

                aimUp: "8",
                aimDown: "5",
                aimLeft: "4",
                aimRight: "6"
            }
        );


        updateWeapons();
        updateBullets();

    }


    const cam =
        getCamera();


    /* 배경 */

    ctx.fillStyle = "#4f913f";

    ctx.fillRect(
        0,
        0,
        SCREEN_W,
        SCREEN_H
    );


    /* 도로 */

    const roadY =
        1000 - cam.y;


    ctx.fillStyle = "#666";

    ctx.fillRect(
        0,
        roadY,
        SCREEN_W,
        220
    );


    /* 도로 선 */

    ctx.fillStyle = "#e5dfaa";


    for (
        let x = -cam.x % 100;
        x < SCREEN_W;
        x += 100
    ) {

        ctx.fillRect(
            x,
            roadY + 105,
            50,
            10
        );

    }


    /* 구조물 */

    for (const o of obstacles) {

        drawObstacle(
            o,
            cam
        );

    }


    drawWeapons(cam);

    drawBullets(cam);

    drawPlayer(p1, cam);
    drawPlayer(p2, cam);

    drawUI();

    drawGameOver();


    requestAnimationFrame(
        gameLoop
    );

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
