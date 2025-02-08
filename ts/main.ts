function load() {
    window.addEventListener("resize", updateHeight)
    updateHeight()

    startCamera()
    startGame()
}

function updateHeight() {
    document.body.style.height = `${window.innerHeight}px`
}
