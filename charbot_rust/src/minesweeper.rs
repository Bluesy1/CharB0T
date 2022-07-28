mod field;
pub mod game;
mod common;
use pyo3::prelude::*;

pub(crate) fn register_minesweeper(_py: Python, m: &PyModule) -> PyResult<()> {
    //let tictactoe = PyModule::new(py, "tictactoe")?;
    m.add_class::<game::Game>()?;
    m.add_class::<game::ChordResult>()?;
    m.add_class::<game::RevealResult>()?;
    //let all = [
    //    "Game",
    //    "Piece",
    //    "Offset",
    //];
    //let pyall = PyTuple::new(py, all.into_iter());
    //tictactoe.add("__all__", pyall)?;
    //tictactoe.add("__doc__", DOCSTRING)?;
    //m.add_submodule(tictactoe)?;
    Ok(())
}
