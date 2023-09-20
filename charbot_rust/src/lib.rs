// COV_EXCL_START COV_EXCL_LINE
use pyo3::prelude::*;
mod tictactoe;
mod points;
mod minesweeper;
mod fluent;

/// A rewrite of parts of charbot in rust.
#[pymodule]
#[pyo3(name = "charbot_rust")]
fn charbot_rust(py: Python, m: &PyModule) -> PyResult<()> {
    tictactoe::register_tictactoe(py, m)?;
    minesweeper::register_minesweeper(py, m)?;
    fluent::register_fluent(m)?;
    Ok(())
}
// COV_EXCL_STOP
