import Vec from "./vector.js";
import {GAME_LEVELS} from "./levels.js"

class Level {
    constructor(plan) {
        let rows = plan.trim().split('\n').map(l=>[...l]);
        this.height = rows.length;
        this.width = rows[0].length;
        this.startActors = [];
            
        this.rows = rows.map((row,y) => {
            return row.map((ch, x) =>
                {let type = levelChars[ch];
                if (typeof type == "string") return type;
                this.startActors.push(
                    type.create(new Vec(x, y), ch));
                return "empty";
            })
        })
    }
}



class State {
    constructor(level, actors, status) {
      this.level = level;
      this.actors = actors;
      this.status = status;
    }
  
    static start(level) {
      return new State(level, level.startActors, "playing");
    }
  
    get player() {
      return this.actors.find(a => a.type == "player");
    }
}

class Player {
    constructor(pos, speed) {
      this.pos = pos;
      this.speed = speed;
    }
  
    get type() { return "player"; }
  
    static create(pos) {
      return new Player(pos.add(new Vec(0, -0.5)),
                        new Vec(0, 0));
    }
}
  
  Player.prototype.size = new Vec(0.8, 1.5);

  class Lava {
    constructor(pos, speed, reset) {
      this.pos = pos;
      this.speed = speed;
      this.reset = reset;
    }
  
    get type() { return "lava"; }
  
    static create(pos, ch) {
      if (ch == "=") {
        return new Lava(pos, new Vec(2, 0));
      } else if (ch == "|") {
        return new Lava(pos, new Vec(0, 2));
      } else if (ch == "v") {
        return new Lava(pos, new Vec(0, 3), pos);
      }
    }
}
  
Lava.prototype.size = new Vec(1, 1);

class Coin {
    constructor(pos, basePos, wobble) {
      this.pos = pos;
      this.basePos = basePos;
      this.wobble = wobble;
    }
  
    get type() { return "coin"; }
  
    static create(pos) {
      let basePos = pos.add(new Vec(0.2, 0.1));
      return new Coin(basePos, basePos,
                      Math.random() * Math.PI * 2);
    }
}

Coin.prototype.size = new Vec(0.6, 0.6);

class Monster {
  constructor(pos, speed, time) { this.pos = pos; this.speed = speed; this.time = time}

  get type() { return "monster"; }

  static create(pos) {
    return new Monster(pos.add(new Vec(0, -1)), new Vec(1, 0), Math.random()*1000);
  }

  update(time, state) {
    let xSpeed = this.speed.get(0)
    let pos = this.pos;
    let movedX = this.pos.add(new Vec(xSpeed * time, 0));
    let movedY = pos.add(new Vec(0, (this.speed.get(1) + time * gravity) * time));
    if (!state.level.touches(movedX, this.size, "wall") && state.level.touches(movedY, this.size, "wall")) {
      pos = movedX;
    }
    else  {
      xSpeed = this.speed.times(-1).get(0)
      movedX = this.pos.add(new Vec(xSpeed * time, 0));
      pos = movedX;
    }
    return new Monster(pos, new Vec(xSpeed, 0))
  }

  collide(state, time) {
    let filtered = state.actors.filter(a => a != this)
    if ((state.player.pos.get(1) + state.player.size.get(1) - state.player.speed.get(1)*tofix1 < this.speed.get(1)) && state.player.speed.get(1)>0) {
      return new State(state.level, filtered, "playing")}
    else {return new State(state.level, state.actors, "lost");}
  }
}

Monster.prototype.size = new Vec(1.2, 2);



const levelChars = {
    ".": "empty", "#": "wall", "+": "lava",
    "@": Player, "o": Coin,
    "=": Lava, "|": Lava, "v": Lava,
    "M": Monster
};


function elt(name, attrs, ...children) {
    let dom = document.createElement(name);
    for (let attr of Object.keys(attrs)) {
      dom.setAttribute(attr, attrs[attr]);
    }
    for (let child of children) {
      dom.appendChild(child);
    }
    return dom;
}

class DOMDisplay {
    constructor(parent, level) {
        this.dom = elt("div", {class: "game"}, drawGrid(level));
        this.actorLayer = null;
        parent.appendChild(this.dom);
    }

    clear() { this.dom.remove(); }
}

const scale = 20;

function drawGrid(level) {
  return elt("table", {
    class: "background",
    style: `width: ${level.width * scale}px`
  }, ...level.rows.map(row =>
    elt("tr", {style: `height: ${scale}px`},
        ...row.map(type => elt("td", {class: type})))
  ));
}

function drawActors(actors) {
    return elt("div", {}, ...actors.map(actor => {
      let rect = elt("div", {class: `actor ${actor.type}`});
      rect.style.width = `${actor.size.get(0) * scale}px`;
      rect.style.height = `${actor.size.get(1) * scale}px`;
      rect.style.left = `${actor.pos.get(0) * scale}px`;
      rect.style.top = `${actor.pos.get(1) * scale}px`;
      return rect;
    }));
}

DOMDisplay.prototype.syncState = function(state) {
    if (this.actorLayer) this.actorLayer.remove();
    this.actorLayer = drawActors(state.actors);
    this.dom.appendChild(this.actorLayer);
    this.dom.className = `game ${state.status}`;
    this.scrollPlayerIntoView(state);
  };


DOMDisplay.prototype.scrollPlayerIntoView = function(state) {
    let width = this.dom.clientWidth;
    let height = this.dom.clientHeight;
    let margin = width / 3;

    // The viewport
    let left = this.dom.scrollLeft, right = left + width;
    let top = this.dom.scrollTop, bottom = top + height;

    let player = state.player;
    let center = player.pos.add(player.size.times(0.5)).times(scale);

    if (center.get(0) < left + margin) {
        this.dom.scrollLeft = center.get(0) - margin;
    } else if (center.get(0) > right - margin) {
        this.dom.scrollLeft = center.get(0) + margin - width;
    }
    if (center.get(1) < top + margin) {
        this.dom.scrollTop = center.get(1) - margin;
    } else if (center.get(1) > bottom - margin) {
        this.dom.scrollTop = center.get(1) + margin - height;
    }
};  

Level.prototype.touches = function(pos,size,type) {
  var xStart = Math.floor(pos.get(0));
  var xEnd = Math.ceil(pos.get(0)+size.get(0));
  var yStart = Math.floor(pos.get(1));
  var yEnd = Math.ceil(pos.get(1)+size.get(1));
  for (var y = yStart; y < yEnd; y++) {
    for (var x = xStart; x < xEnd; x++) {
      let isOutside = x < 0 || x >= this.width ||
                      y < 0 || y >= this.height;
      let here = isOutside ? "wall" : this.rows[y][x];
      if (here == type) return true;
    }
  }
  return false;
};

State.prototype.update = function(time, keys) {
  let actors = this.actors.map(actor => actor.update(time, this, keys));
  let newState = new State(this.level, actors, this.status);
  if (newState.status != "playing") return newState;

  let player = newState.player;
  if (this.level.touches(player.pos, player.size, "lava")) {
    return new State(this.level, actors, "lost");
  }
  for (let actor of actors) {
    if (actor != player && overlap(actor,player)) {
      newState = actor.collide(newState, time)
    }
  }
  return newState;
}

function overlap(actor1, actor2) {
  return actor1.pos.get(0) + actor1.size.get(0) > actor2.pos.get(0) &&
         actor1.pos.get(0) < actor2.pos.get(0) + actor2.size.get(0) &&
         actor1.pos.get(1) + actor1.size.get(1) > actor2.pos.get(1) &&
         actor1.pos.get(1) < actor2.pos.get(1) + actor2.size.get(1);
}

Lava.prototype.collide = function(state) {
  return new State(state.level, state.actors, "lost");
};

Coin.prototype.collide = function(state) {
  let filtered = state.actors.filter(a => a != this);
  let status = state.status;
  if (!filtered.some(a => a.type == "coin")) status = "won";
  return new State(state.level, filtered, status);
};

Lava.prototype.update = function(time, state) {
  let newPos=this.pos.add(this.speed.times(time))
  if (!state.level.touches(newPos, this.size, "wall")) {
    return new Lava(newPos,this.speed,this.reset)
  }
  else if (this.reset) {
    return new Lava(this.reset, this.speed, this.reset);
  } else {
    return new Lava(this.pos, this.speed.times(-1));
  }
};

const playerXSpeed = 7;
const gravity = 30;
const jumpSpeed = 17;

Player.prototype.update = function(time, state, keys) {
  let xSpeed = 0;
  if (keys.ArrowLeft) xSpeed -= playerXSpeed;
  if (keys.ArrowRight) xSpeed += playerXSpeed;
  let pos = this.pos;
  let movedX = pos.add(new Vec(xSpeed * time, 0));
  if (!state.level.touches(movedX, this.size, "wall")) {
    pos = movedX;
  }

  let ySpeed = this.speed.get(1) + time * gravity;
  let movedY = pos.add(new Vec(0, ySpeed * time));
  if (!state.level.touches(movedY, this.size, "wall")) {
    pos = movedY;
  } else if (keys.ArrowUp && ySpeed > 0) {
    ySpeed = -jumpSpeed;
  } else {
    ySpeed = 0;
  }
  return new Player(pos, new Vec(xSpeed, ySpeed));
};

const wobbleSpeed = 8, wobbleDist = 0.07;

Coin.prototype.update = function(time) {
  let wobble = this.wobble + time * wobbleSpeed;
  let wobblePos = Math.sin(wobble) * wobbleDist;
  return new Coin(this.basePos.add(new Vec(0, wobblePos)),
                  this.basePos, wobble);
};

var tracker;
function trackKeys(keys) {
  let down = Object.create(null);
  function track(event) {
    if (keys.includes(event.key)) {
      down[event.key] = event.type == "keydown";
      event.preventDefault();
    }
  }
  tracker = track;
  addKeys()
  return down;
}

function addKeys() {
  window.addEventListener("keydown", tracker);
  window.addEventListener("keyup", tracker);
}

function removeKeys() {
  window.removeEventListener("keydown", tracker)
  window.removeEventListener("keyup", tracker)
}

const arrowKeys =
  trackKeys(["ArrowLeft", "ArrowRight", "ArrowUp"]);


function runAnimation(frameFunc) {
  let lastTime = null;
  function frame(time) {
    if (lastTime != null) {
      let timeStep = Math.min(time - lastTime, 100) / 1000;
      if (frameFunc(timeStep) === false) return;
    }
    lastTime = time;
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}



function runLevel(level, Display) {
  let display = new Display(document.getElementById("demo"), level);
  var state = State.start(level);
  let ending = 1;
  var paused = false;
  var resolvefunction;
  function pause(event) {
    debugger;
    if (event.key=="Escape") {
      if (paused == true){
        paused = false;
        addKeys();
        runAnimation(processor)
      }
      else if (paused == false) {
        paused = true;
        removeKeys();
      }
    }
  }
  window.addEventListener("keydown", pause)
  function processor(time) {
    state = state.update(time, arrowKeys);
    display.syncState(state);
    if (paused) {return false}
    if (state.status == "playing") {
      return true;
    } else if (ending > 0) {
      ending -= time;
      return true;
    } else {
      display.clear();
      resolvefunction(state.status);
      return false;
    }
  }
  return new Promise(resolve => {
    resolvefunction = resolve;
    runAnimation(processor);
  })
}

async function runGame(plans, Display) {
  for (let level = 0; level < plans.length;) {
    let status = await runLevel(new Level(plans[level]),
                                Display);
    if (status == "won") level++;
  }
  removeKeys();
  
  document.body.appendChild(document.createTextNode("You've Won!"))
  console.log("You've won!");
}

var tofix1 = 3.5;
runGame(GAME_LEVELS, DOMDisplay)