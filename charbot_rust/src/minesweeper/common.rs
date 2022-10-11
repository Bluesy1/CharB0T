/*#[derive(PartialEq)]
pub enum ParamType {
    Width,
    Height,
    Mines,
}*/

pub enum MoveDestination {
    Up,
    Down,
    Left,
    Right,
}

pub const LABEL_A: &'static [u8] = include_bytes!("labels/A.png");
pub const LABEL_B: &'static [u8] = include_bytes!("labels/B.png");
pub const LABEL_C: &'static [u8] = include_bytes!("labels/C.png");
pub const LABEL_D: &'static [u8] = include_bytes!("labels/D.png");
pub const LABEL_E: &'static [u8] = include_bytes!("labels/E.png");
pub const LABEL_F: &'static [u8] = include_bytes!("labels/F.png");
pub const LABEL_G: &'static [u8] = include_bytes!("labels/G.png");
pub const LABEL_H: &'static [u8] = include_bytes!("labels/H.png");
pub const LABEL_I: &'static [u8] = include_bytes!("labels/I.png");
pub const LABEL_J: &'static [u8] = include_bytes!("labels/J.png");
pub const LABEL_K: &'static [u8] = include_bytes!("labels/K.png");
pub const LABEL_L: &'static [u8] = include_bytes!("labels/L.png");
pub const LABEL_M: &'static [u8] = include_bytes!("labels/M.png");
pub const LABEL_N: &'static [u8] = include_bytes!("labels/N.png");
pub const LABEL_O: &'static [u8] = include_bytes!("labels/O.png");
pub const LABEL_P: &'static [u8] = include_bytes!("labels/P.png");
pub const LABEL_Q: &'static [u8] = include_bytes!("labels/Q.png");
pub const LABEL_R: &'static [u8] = include_bytes!("labels/R.png");
pub const LABEL_S: &'static [u8] = include_bytes!("labels/S.png");
pub const LABEL_T: &'static [u8] = include_bytes!("labels/T.png");
pub const LABEL_U: &'static [u8] = include_bytes!("labels/U.png");
pub const LABEL_V: &'static [u8] = include_bytes!("labels/V.png");
pub const LABEL_W: &'static [u8] = include_bytes!("labels/W.png");
pub const LABEL_X: &'static [u8] = include_bytes!("labels/X.png");
pub const LABEL_Y: &'static [u8] = include_bytes!("labels/Y.png");

pub const TILE_1: &'static [u8] = include_bytes!("tiles/1.png");
pub const TILE_2: &'static [u8] = include_bytes!("tiles/2.png");
pub const TILE_3: &'static [u8] = include_bytes!("tiles/3.png");
pub const TILE_4: &'static [u8] = include_bytes!("tiles/4.png");
pub const TILE_5: &'static [u8] = include_bytes!("tiles/5.png");
pub const TILE_6: &'static [u8] = include_bytes!("tiles/6.png");
pub const TILE_7: &'static [u8] = include_bytes!("tiles/7.png");
pub const TILE_8: &'static [u8] = include_bytes!("tiles/8.png");
pub const TILE_DEFAULT: &'static [u8] = include_bytes!("tiles/default.png");
pub const TILE_EMPTY: &'static [u8] = include_bytes!("tiles/empty.png");
pub const TILE_FLAG: &'static [u8] = include_bytes!("tiles/flag.png");
pub const TILE_MINE_EXPLODED: &'static [u8] = include_bytes!("tiles/mine1.png");
pub const TILE_MINE_UNEXPLODED: &'static [u8] = include_bytes!("tiles/mine2.png");
pub const TILE_MINE_TRIGGER: &'static [u8] = include_bytes!("tiles/mine3.png");

#[cfg(test)]
mod tests {
    use super::*;
    use yare::parameterized;
    #[parameterized(
        a={LABEL_A, "Tile A"},
        b={LABEL_B, "Tile B"},
        c={LABEL_C, "Tile C"},
        d={LABEL_D, "Tile D"},
        e={LABEL_E, "Tile E"},
        f={LABEL_F, "Tile F"},
        g={LABEL_G, "Tile G"},
        h={LABEL_H, "Tile H"},
        i={LABEL_I, "Tile I"},
        j={LABEL_J, "Tile J"},
        k={LABEL_K, "Tile K"},
        l={LABEL_L, "Tile L"},
        m={LABEL_M, "Tile M"},
        n={LABEL_N, "Tile N"},
        o={LABEL_O, "Tile O"},
        p={LABEL_P, "Tile P"},
        q={LABEL_Q, "Tile Q"},
        r={LABEL_R, "Tile R"},
        s={LABEL_S, "Tile S"},
        t={LABEL_T, "Tile T"},
        u={LABEL_U, "Tile U"},
        v={LABEL_V, "Tile V"},
        w={LABEL_W, "Tile W"},
        x={LABEL_X, "Tile X"},
        y={LABEL_Y, "Tile Y"},
        one={TILE_1, "Tile 1"},
        two={TILE_2, "Tile 2"},
        three={TILE_3, "Tile 3"},
        four={TILE_4, "Tile 4"},
        five={TILE_5, "Tile 5"},
        six={TILE_6, "Tile 6"},
        seven={TILE_7, "Tile 7"},
        eight={TILE_8, "Tile 8"},
        default={TILE_DEFAULT, "Default Tile"},
        empty={TILE_EMPTY, "Empty Tile"},
        flag={TILE_FLAG, "Flag Tile"},
        mine_exploded={TILE_MINE_EXPLODED, "Exploded Mine Tile"},
        mine_unexploded={TILE_MINE_UNEXPLODED, "Unexploded Mine Tile"},
        mine_trigger={TILE_MINE_TRIGGER, "Trigger Mine Tile"},
    )]
    fn images_exist(img: &'static [u8], name: &str) {
        assert!(img.len() > 0, "{} is empty/missing.", name);
    }
}
