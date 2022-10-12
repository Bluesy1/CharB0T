// SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
// SPDX-License-Identifier: MIT
// COV_EXCL_START COV_EXCL_LINE
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
// COV_EXCL_STOP
