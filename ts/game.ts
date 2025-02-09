var state: State
var gameCanvas: HTMLCanvasElement
var gameContext: CanvasRenderingContext2D
var images: Map<string, HTMLImageElement> = new Map()

const renderScale: number = 32
const sideTapProximity: number = 128
const sideMoveProximity: number = 2

var messageTimeoutID: number | undefined = undefined
var moveWaitTimeoutID: number | undefined = undefined

var cam = { x: 0, y: 0 }

function startGame() {
    gameCanvas = document.getElementById("game") as HTMLCanvasElement
    gameContext = gameCanvas.getContext("2d")!

    gameCanvas.addEventListener("click", handleGameClick)
    document.querySelectorAll("span.item")
        .forEach(item => {
            (item as HTMLElement).addEventListener("click", handleClickItem)
        })

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

async function sendAction(url: string): Promise<State> {
    return fetch(url, {
            "method": "POST"
        })
        .then(r => r.json())
        .then(j => {
            if (j.message) {
                showMessage(j.message)
            }

            if (!j.ok) {
                return Promise.reject(new Error("Action was not successful"))
            }
        })
        .then(fetchState)
        .catch(err => state)
}

function showMessage(message: string, timeout: number = 5000) {
    var box = document.getElementById("message-box")!

    if (!box.hidden) {
        box.hidden = true

        if (messageTimeoutID !== undefined) {
            clearTimeout(messageTimeoutID)
        }

        setTimeout(() => showMessage(message), 200)
    } else {
        box.textContent = message
        box.hidden = false

        messageTimeoutID = setTimeout(() => {
            box.hidden = true
        }, timeout)
    }
}

function handleClickItem(event: MouseEvent) {
    const el = event.target as HTMLElement
    const index = el.getAttribute("data-index")

    sendAction(`/api/select-item/${index}`)
}

function handleGameClick(event: MouseEvent) {
    const rect = gameCanvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    let direction

    if (x < sideTapProximity) direction = "l"
    else if (x > rect.width - sideTapProximity) direction = "r"
    else if (y < sideTapProximity) direction = "u"
    else if (y > rect.height - sideTapProximity) direction = "d"

    if (direction) {
        move(direction)
    }
}

function setWaitMessage(message: string, timeout: number = 10000) {
    if (moveWaitTimeoutID !== undefined) {
        clearTimeout(moveWaitTimeoutID)
        moveWaitTimeoutID = undefined
    }

    moveWaitTimeoutID = setTimeout(() =>
        showMessage(message, timeout), 250)
}

function move(direction: string) {
    setWaitMessage("Processing...")

    sendAction(`/api/move-player/${direction}`)
        .finally(() => clearTimeout(moveWaitTimeoutID))
}

function getRealCameraPosition(): { x: number, y: number } {
    var tilesWide = Math.floor(gameCanvas.clientWidth / renderScale)
    var tilesHigh = Math.floor(gameCanvas.clientHeight / renderScale)
    var dx = cam.x - state.player.x
    var dy = cam.y - state.player.y

    if (dx < sideMoveProximity - tilesWide / 2) cam.x += 1
    if (dx > tilesWide / 2 - sideMoveProximity) cam.x -= 1
    if (dy < sideMoveProximity - tilesHigh / 2) cam.y += 1
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
    renderInventory()

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
            const img = images.get(tile.img)
            if (img !== undefined) {
                gameContext.drawImage(img, 0, 0, img.width, img.height, x, y, 1, 1)
            }
        }
    }
}

function renderInventory() {
    var inv = state.player.items
    var selected = state.player.selected_item

    var container = document.getElementById("inventory")!
    var items = Array.from(container.children)

    for (var i = 0; i < items.length; i++){
        var itemEl = items[i] as HTMLElement
        itemEl.classList.toggle("active", i == selected)

        if (i < inv.length) {
            var item = inv[i]

            itemEl.textContent = item
        } else {
            itemEl.textContent = "-"
        }
    }
}

async function preloadImages(): Promise<Map<string, HTMLImageElement>> {
    var toLoad: Set<string> = new Set([
        "/static/img/player.png",
        "/static/img/tiles/open_door.png",
        "/static/img/tiles/closed_door.png",
    ])

    state.map.tiles.forEach(row => row.forEach(tile => {
        const src = tile.img
        if (!images.has(src) && src != "") {
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
