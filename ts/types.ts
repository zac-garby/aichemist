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

interface State {
    map: TileMap
    player_x: number
    player_y: number
}
