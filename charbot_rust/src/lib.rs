// GCOVR_EXCL_START
use pyo3::prelude::*;
mod tictactoe;
mod points;
mod minesweeper;

/// A rewrite of parts of charbot in rust.
#[pymodule]
#[pyo3(name = "charbot_rust")]
fn charbot_rust(py: Python, m: &PyModule) -> PyResult<()> {
    tictactoe::register_tictactoe(py, m)?;
    minesweeper::register_minesweeper(py, m)?;
    Ok(())
}
// GCOVR_EXCL_STOP
