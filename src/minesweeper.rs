mod field; // COV_EXCL_LINE
pub mod game;
mod common;
// COV_EXCL_START
use pyo3::prelude::*;

const DOCSTRING: &str = "Rust based re-implementation of minesweeper";

pub(crate) fn register_minesweeper(parent_module: &Bound<PyModule>) -> PyResult<()> {
    let minesweeper = PyModule::new(parent_module.py(), "_minesweeper")?;
    minesweeper.add_class::<game::Game>()?;
    minesweeper.add_class::<game::ChordResult>()?;
    minesweeper.add_class::<game::RevealResult>()?;
    minesweeper.add("__doc__", DOCSTRING)?;
    parent_module.add_submodule(&minesweeper)?;
    Ok(())
}
// COV_EXCL_STOP
