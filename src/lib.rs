// COV_EXCL_START COV_EXCL_LINE
use pyo3::prelude::*;
mod tictactoe;
mod points;
mod minesweeper;

/// A rewrite of parts of charbot in rust.
#[pymodule]
#[pyo3(name = "_rust")]
fn _rust(m: &Bound<PyModule>) -> PyResult<()> {
    tictactoe::register_tictactoe(m)?;
    minesweeper::register_minesweeper(m)?;
    Ok(())
}
// COV_EXCL_STOP
