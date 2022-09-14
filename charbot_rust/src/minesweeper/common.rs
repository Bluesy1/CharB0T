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
    #[test]
    fn images_exist(){
        assert!(LABEL_A.len() > 0);
        assert!(LABEL_B.len() > 0);
        assert!(LABEL_C.len() > 0);
        assert!(LABEL_D.len() > 0);
        assert!(LABEL_E.len() > 0);
        assert!(LABEL_F.len() > 0);
        assert!(LABEL_G.len() > 0);
        assert!(LABEL_H.len() > 0);
        assert!(LABEL_I.len() > 0);
        assert!(LABEL_J.len() > 0);
        assert!(LABEL_K.len() > 0);
        assert!(LABEL_L.len() > 0);
        assert!(LABEL_M.len() > 0);
        assert!(LABEL_N.len() > 0);
        assert!(LABEL_O.len() > 0);
        assert!(LABEL_P.len() > 0);
        assert!(LABEL_Q.len() > 0);
        assert!(LABEL_R.len() > 0);
        assert!(LABEL_S.len() > 0);
        assert!(LABEL_T.len() > 0);
        assert!(LABEL_U.len() > 0);
        assert!(LABEL_V.len() > 0);
        assert!(LABEL_W.len() > 0);
        assert!(LABEL_X.len() > 0);
        assert!(LABEL_Y.len() > 0);
        assert!(TILE_1.len() > 0);
        assert!(TILE_2.len() > 0);
        assert!(TILE_3.len() > 0);
        assert!(TILE_4.len() > 0);
        assert!(TILE_5.len() > 0);
        assert!(TILE_6.len() > 0);
        assert!(TILE_7.len() > 0);
        assert!(TILE_8.len() > 0);
        assert!(TILE_DEFAULT.len() > 0);
        assert!(TILE_EMPTY.len() > 0);
        assert!(TILE_FLAG.len() > 0);
        assert!(TILE_MINE_EXPLODED.len() > 0);
        assert!(TILE_MINE_UNEXPLODED.len() > 0);
        assert!(TILE_MINE_TRIGGER.len() > 0);
    }
}
