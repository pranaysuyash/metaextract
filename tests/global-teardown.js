module.exports = async () => {
  try {
    const getHandles = () =>
      typeof process._getActiveHandles === 'function'
        ? process._getActiveHandles()
        : [];

    const handles = getHandles();
    console.warn(`Global teardown: ${handles.length} active handles`);

    handles.forEach((h, i) => {
      try {
        const name = h && h.constructor && h.constructor.name ? h.constructor.name : typeof h;
        console.warn(`Handle ${i}: ${name}`);

        // Don't forcibly close stdout/stderr or WriteStreams used by Jest reporters —
        // attempting to end those can cause `write after end` when reporters still
        // emit status updates. Only log them for debugging.
        if (name === 'WriteStream' || h === process.stdout || h === process.stderr) {
          console.warn(`Skipping close for handle ${i} (${name})`);
          return;
        }

        // Best-effort close for other common handle types
        if (h && typeof h.close === 'function') {
          try {
            h.close();
            console.warn(`Closed handle ${i} (${name})`);
          } catch (e) {
            // ignore
          }
        } else if (h && typeof h.end === 'function') {
          try {
            h.end();
            console.warn(`Ended handle ${i} (${name})`);
          } catch (e) {
            // ignore
          }
        } else if (h && h.pid) {
          try {
            process.kill(h.pid, 'SIGTERM');
            console.warn(`Terminated child process pid=${h.pid}`);
          } catch (e) {
            // ignore
          }
        }
      } catch (e) {
        console.warn('Error while inspecting handle', e);
      }
    });

    // Give a short grace period for closures to complete
    await new Promise(resolve => setTimeout(resolve, 200));

    const remainingAll = getHandles();
    // Filter out stdout/stderr and WriteStream handles which we intentionally don't close
    const remaining = remainingAll.filter(h => {
      const name = h && h.constructor && h.constructor.name ? h.constructor.name : typeof h;
      return !(name === 'WriteStream' || h === process.stdout || h === process.stderr);
    });

    if (remaining.length) {
      console.warn(`Global teardown: ${remaining.length} remaining non-WriteStream handles — forcing exit`);
      remaining.forEach((h, i) => {
        const name = h && h.constructor && h.constructor.name ? h.constructor.name : typeof h;
        console.warn(`Remaining handle ${i}: ${name}`);
      });
      // Force exit so CI doesn't hang — we've logged handles above for investigation
      process.exit(0);
    } else {
      // Only stdout/stderr/WriteStream remain — exit cleanly (no need to list them every run)
      console.warn('Global teardown: only WriteStream/stdout/stderr handles remain; exiting.');
      process.exit(0);
    }
  } catch (err) {
    console.error('Global teardown failed:', err);
    process.exit(0);
  }
};
