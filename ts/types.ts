interface Tile {
    class: string
    passable: boolean
    img: string
}

interface TileMap {
    width: number
    height: number
    tiles: Array<Array<Tile>>
}

interface Player {
    x: number
    y: number
    img: string
}

interface State {
    map: TileMap
    player: Player
}
