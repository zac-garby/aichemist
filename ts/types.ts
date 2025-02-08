interface Tile {
    class: string
    passable: boolean
    img: string
}

interface TileMap {
    width: number
    height: number
    tiles: Tile[][]
}

interface Player {
    x: number
    y: number
    img: string
    items: string[]
    selected_item: number | null
}

interface State {
    map: TileMap
    player: Player
}
