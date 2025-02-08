var state: State
var gameCanvas: HTMLCanvasElement
var gameContext: CanvasRenderingContext2D
var images: Map<string, HTMLImageElement> = new Map()

const renderScale: number = 64
const sideTapProximity: number = 128
const sideMoveProximity: number = 1

var cam = { x: 0, y: 0 }

function startGame() {
    gameCanvas = document.getElementById("game") as HTMLCanvasElement
    gameContext = gameCanvas.getContext("2d")!

    gameCanvas.addEventListener("click", handleGameClick)

    fetchState()
        .then(preloadImages)
        .then(_ => {
            cam.x = state.player.x
            cam.y = state.player.y
        })
        .then(render)
}

async function fetchState(): Promise<State> {
    return fetch("/api/state")
        .then(r => r.json())
        .then(j => {
            state = j.state
            return state
        })
}

function handleGameClick(event: MouseEvent) {
    const rect = gameCanvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    if (x < sideTapProximity) state.player.x += -1
    else if (x > rect.width - sideTapProximity) state.player.x += 1
    else if (y < sideTapProximity) state.player.y += -1
    else if (y > rect.height - sideTapProximity) state.player.y += 1
}

function getRealCameraPosition(): { x: number, y: number } {
    var tilesWide = Math.floor(gameCanvas.clientWidth / renderScale)
    var tilesHigh = Math.floor(gameCanvas.clientHeight / renderScale)
    var dx = cam.x - state.player.x
    var dy = cam.y - state.player.y

    if (dx < sideMoveProximity - 1 - tilesWide / 2) cam.x += 1
    if (dx > tilesWide / 2 - sideMoveProximity) cam.x -= 1
    if (dy < sideMoveProximity - 1 - tilesHigh / 2) cam.y += 1
    if (dy > tilesHigh / 2 - sideMoveProximity) cam.y -= 1

    return {
        x: Math.floor(tilesWide / 2) - cam.x,
        y: Math.floor(tilesHigh / 2) - cam.y
    }
}

function resetCanvas() {
    const dpr = window.devicePixelRatio || 1.0
    gameCanvas.width = gameCanvas.clientWidth * dpr
    gameCanvas.height = gameCanvas.clientHeight * dpr
    gameContext.scale(renderScale * dpr, renderScale * dpr)
    gameContext.imageSmoothingEnabled = false
}

function render() {
    resetCanvas()

    let { x, y } = getRealCameraPosition()
    gameContext.translate(x, y)

    renderMap()
    renderPlayer()
    requestAnimationFrame(render)
}

function renderPlayer() {
    const img = images.get(state.player.img)!
    gameContext.drawImage(img, 0, 0, img.width, img.height, state.player.x, state.player.y, 1, 1)
}

function renderMap() {
    for (let y = 0; y < state.map.height; y++) {
        for (let x = 0; x < state.map.width; x++) {
            const tile = state.map.tiles[y][x]
            const img = images.get(tile.img)!
            gameContext.drawImage(img, 0, 0, img.width, img.height, x, y, 1, 1)
        }
    }
}

async function preloadImages(): Promise<Map<string, HTMLImageElement>> {
    var toLoad: Set<string> = new Set([
        "/static/img/player.png",
    ])

    state.map.tiles.forEach(row => row.forEach(tile => {
        const src = tile.img
        if (!images.has(src)) {
            toLoad.add(src)
        }
    }))

    return Promise.all(Array.from(toLoad).map(
        src => new Promise((resolve, reject) => {
            const img = new Image()
            img.onload = () => {
                images.set(src, img)
                resolve(img)
            }

            img.onerror = () => reject(new Error(`Failed to load image ${src}`))

            img.crossOrigin = "anonymous"
            img.src = src
            img.loading = "eager"
        })
    )).then(_ => images)
}
