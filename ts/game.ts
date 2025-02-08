var state: State
var gameCanvas: HTMLCanvasElement
var gameContext: CanvasRenderingContext2D
var tileImages: Map<string, HTMLImageElement> = new Map()
var renderScale: number = 64

var cam = { x: 0, y: 0 }

function startGame() {
    gameCanvas = document.getElementById("game") as HTMLCanvasElement
    gameContext = gameCanvas.getContext("2d")!

    fetchState()
        .then(preloadTileImages)
        .then(renderMap)
}

async function fetchState(): Promise<State> {
    return fetch("/api/state")
        .then(r => r.json())
        .then(j => {
            state = j.state
            return state
        })
}

function resetCanvas() {
    const dpr = window.devicePixelRatio || 1.0
    gameCanvas.width = gameCanvas.clientWidth * dpr
    gameCanvas.height = gameCanvas.clientHeight * dpr
    gameContext.scale(renderScale * dpr, renderScale * dpr)
    gameContext.imageSmoothingEnabled = false
}

function renderMap() {
    resetCanvas()

    gameContext.translate(-cam.x, -cam.y)

    for (let y = 0; y < state.map.height; y++) {
        for (let x = 0; x < state.map.width; x++) {
            const tile = state.map.tiles[y][x]
            const img = tileImages.get(tile.img)!
            gameContext.drawImage(img, 0, 0, img.width, img.height, x, y, 1, 1)
        }
    }

    requestAnimationFrame(renderMap)
}

async function preloadTileImages(): Promise<Map<string, HTMLImageElement>> {
    var toLoad: Set<string> = new Set()

    state.map.tiles.forEach(row => row.forEach(tile => {
        const src = tile.img
        if (!tileImages.has(src)) {
            toLoad.add(src)
        }
    }))

    return Promise.all(Array.from(toLoad).map(
        src => new Promise((resolve, reject) => {
            const img = new Image()
            img.onload = () => {
                tileImages.set(src, img)
                resolve(img)
            }

            img.onerror = () => reject(new Error(`Failed to load image ${src}`))

            img.crossOrigin = "anonymous"
            img.src = src
            img.loading = "eager"
        })
    )).then(_ => tileImages)
}
