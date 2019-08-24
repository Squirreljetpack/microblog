export default class Vec {
    constructor(...args) {
        let points = [];
        for (var i = 0; i < arguments.length; i++) {
            if (isNaN(arguments[i])) {
                console.log(`Argument ${i} is not a Number. 0 pushed.`)
                points.push(0)
            }
            else {
                points.push(arguments[i]);
            }   
        }
        this.points=points;
        this.dim = arguments.length;
        let total = 0;
        for (var i = 0; i < arguments.length; i++) {
            total+=(arguments[i])**2
        }
        this.length = Math.sqrt(total);
    }
    add(x) {
        if (x instanceof Vec) {
            if (x.dim<=this.dim) {
                let arr =[];
                for (var i = 0; i < x.dim; i++) {
                    arr.push(this.points[i]+x.points[i]);
                }
                for (; i < this.dim; i++) {
                    arr.push(this.points[i]);
                }
                return new Vec(...arr)
            }
        }
        
    }
    subtract(x) {
        if (x instanceof Vec) {
            if (x.dim<=this.dim) {
                let arr =[];
                for (var i = 0; i < x.dim; i++) {
                    arr.push(this.points[i]-x.points[i]);
                }
                for (; i < this.dim; i++) {
                    arr.push(this.points[i]);
                }
                return new Vec(...arr)
            }
        }
    }
    dot(x) {
        result = 0;
        if (x instanceof Vec) {
            if (x.dim==this.dim) {
                for (var i = 0; i < this.dim; i++) {
                    result+=this.points[i]*x.points[i];
                }
            }
            
        }
        return result
    }
    times(factor) {
        let arr =[];
        for (var i = 0; i < this.dim; i++) {
            arr.push(this.points[i]*factor);
        }
        return new Vec(...arr)
    }

    get(index) {
        return this.points[index]
    }
}

// y = new Vec(3,4,6);
// console.log(y.add(new Vec (4,5)));



// module.exports = Vec;
// global.Vec = Vec;

