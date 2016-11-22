

// It appears that I cannot set cookies in testing.
/*
QUnit.test("getCookie", function(assert) {
	var key = "" + Math.random()
	document.cookie = "cookietest=" + key;
	assert.equal(document.cookie, key, "cookie set incorrectly.");
	var check = getCookie("cookietest");
	document.cookie = null;
	assert.equal(check, key, "getcookie returned incorrect value.");
});
*/

// also disabled because I cannot give permission 
/*
QUnit.test("recorder", function(assert) {
	var p = newRecorder()
    p.then(
        function(rec) {
            console.log("Okay.");
        }
    ).catch( 
        function(err) {
            assert.notOk(true, "Failed to get permission.");
        }
    );
});
*/

/** EVENT TESTS */
QUnit.test("Start Event", function(assert) {
    var main = document.createElement("div");
    var right = document.createElement("div");
    var cl = right.classList;
    cl.add("other");
    cl.add("hide");
    cl.add("SideRedButton");
    onStart(main, right);
    assert.equal(main.innerHTML, "STOP", "Didn't change button to stop.");
    assert.equal(right.innerHTML, "PAUSE", "Didn't change button to pause.");
    var cl = right.classList;
    assert.ok(cl.contains("other"), "Removed other class styles.");
    assert.notOk(cl.contains("hide"), "Side button hidden.");
    assert.notOk(cl.contains("SideRedButton"), "Side button still red.");
});

QUnit.test("Pause Event", function(assert) {
    var main = document.createElement("div");
    var left = document.createElement("div");
    var right = document.createElement("div");
    var cl = left.classList;
    cl.add("hide");
    cl.add("other");
    onPause(main, left, right);
    assert.equal(main.innerHTML, "RESUME", "Didn't change button to resume.");
    assert.equal(right.innerHTML, "STOP", "Didn't change button to stop.");
    assert.equal(left.innerHTML, "RESTART", "Didn't change button to restart.");
    assert.ok(cl.contains("other"), "Left removed extra classes.");
    assert.notOk(cl.contains("hide"), "Left still hidden.");
});

QUnit.test("Resume Event", function (assert) {
    var main = document.createElement("div");
    var left = document.createElement("div");
    var right = document.createElement("div");
    var cl = right.classList;
    cl.add("other");
    cl.add("SideRedButton");
    onResume(main, left, right);
    assert.equal(main.innerHTML, "STOP", "Didn't change button to stop");
    assert.equal(right.innerHTML, "PAUSE", "Didn't change right button to pause.");
    assert.ok(left.classList.contains("hide"), "Left button didn't disappear.");
    assert.notOk(cl.contains("SideRedButton"), "Right button still red.");
    assert.ok(cl.contains("other"), "Right button removed other classes.");
});

QUnit.test("Stop Event UI", function(assert) {
    var main = document.createElement("div");
    var left = document.createElement("div");
    var right = document.createElement("div");
    onStop(main, left, right);
    assert.equal(main.innerHTML, "RECORD", "Didn't change main button.");
    assert.ok(left.classList.contains("hide"), "Left button still visible.");
    assert.ok(right.classList.contains("hide"), "Right button still visible.");
});

QUnit.test("Restart Event", function(assert) {
    var main = document.createElement("div");
    var left = document.createElement("div");
    var right = document.createElement("div");
    right.classList.add("SideRedButton");
    right.classList.add("other");
    onRestart(main, left, right);
    assert.equal(main.innerHTML, "RECORD", "Didn't change main button.");
    assert.ok(left.classList.contains("hide"), "Left button still visible.");
    assert.ok(right.classList.contains("hide"), "Right button still visible.");
    assert.ok(right.classList.contains("other"), "Right button removed other classes.");
    assert.notOk(right.classList.contains("SideRedButton"), "Right button still red.");
});

