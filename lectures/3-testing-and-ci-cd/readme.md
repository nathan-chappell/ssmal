# Lecture 3: Testing and CI/CD

## CI/CD

__COMMENT__: I've tried reading some books on this topic, and found them not to be particularly helpful.
The notions are too vague to be interesting abstractly (at least for a whole book's worth of information),
and practices are too specific or obvious to go into any detail about.

__NOTE__: Some things aren't worth being an expert on.  We'll be happy with Wikipedia and some examples...

According to [wikipedia CI/CD:](https://en.wikipedia.org/wiki/CI/CD)

* Continuous Integration: Frequent merging of several small changes into a main branch
* Continuous delivery: When teams produce software in short cycles so that software can be released with a simple and repeatable deployment process
* Continuous deployment: When new software functionality is rolled out completely automatically

__My Experience__: I've never seen "real" CI/CD done (just like I've never seen "real" extreme-programming or TDD...).
But even if we aren't ideological zealots, we can still take the basic ideas and apply them to our work for our benefit.

* Avoid broad, concurrent changes to the application
* Automated tests
* Dealing with different configurations and VCS
* Automated building for different configurations
* If possible, this should be done *locally* (workstation) and *centrally* (CI/CD server)

If we translate these ideas into concrete tasks...

* Don't let some branch go too far without merging it into `develop`
* Write tests you lazy...
* We will probably need to spend an unreasonable amount of our lifespan trying to figure out how poorly documented, unnecessarily complex, and temperamental build-tools work
* Then, after you figure out how to do all this, you need to learn a scripting language so you can do it all in a repeatable, automatic way

Skills:

* `git`
* test runners: pytest, \[NX\]Unit, jest
* build systems: setuptools, make, webpack, msbuild, maven
* package managers:

## Intro to Testing

* why write tests
* different types of tests
* when you __SHOULD__ write tests
* when you __SHOULD NOT__ (think you need to) write tests
* TDD?

### Considerations for Writing Tests

## CI/CD

* definitions

### Github Actions

* walkthrough what I've done on my project...

# Assignment:

<!-- TODO: come up with a simple refactor, students should successfully push... -->