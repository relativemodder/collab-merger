class App {

    workspaceName_ = 'Open'
    get workspaceName() {
        return this.workspaceName_
    }
    set workspaceName(value) {
        this.workspaceName_ = value

        let spinner = `<span class="spinner-border spinner-border-sm workspaceNameLoader" data-bs-toggle="tooltip" data-bs-placement="bottom" data-bs-title="Loading level from saves..." role="status" aria-hidden="true"></span>`

        $('#workspaceName').html(`${spinner} ${value}`)
        $('.workspaceNameLoader').show()
        
        $('.workspaceNameLoader').tooltip()
    }

    changeWaitingForOpeningLevelModalState = (state) => $('#waitingForOpeningLevelModal').modal(state ? 'show' : 'hide')

    onEditorStateChange = (event) => {

        console.log(event)

        this.changeWaitingForOpeningLevelModalState(!event.is_in_editor)
        this.workspaceName = event.editor_level_name !== null ? event.editor_level_name : ""

        if (this.workspaceName != "") {
            this.loadLevelOnOtherSide(this.workspaceName).then(() => {
                $('.workspaceNameLoader').hide()
                console.log(`Loaded level ${this.workspaceName}`)
            })
        }
    }

    getFullTime = (timestamp) => {
        const rounded_to_ms = timestamp.toFixed(3)
        const ms = Number(rounded_to_ms.toString().split('.')[1])
        const m = timestamp >= 60 ? Math.round(timestamp / 60) : 0
        const s = Math.round(rounded_to_ms) - m * 60
        return {
            m: m,
            s: s,
            ms: ms
        }
    }

    formatTime = (timestamp) => {
        const fulltime = this.getFullTime(timestamp)
        return `${fulltime.m.toString().padStart(2, '0')}:${fulltime.s.toString().padStart(2, '0')}.${fulltime.ms}`
    }

    changeOverviewInfo = (levelName, levelLength, levelObjectsCount) => {
        $('p.objects-count').html(`Objects: ${levelObjectsCount}`);
        $('p.level-length').html(`Length: ${this.formatTime(levelLength)}`);

        $('p.objects-count').removeClass('gradient');
        $('p.level-length').removeClass('gradient');
    }

    onLevelLoad = (levelInfo) => {
        console.log(levelInfo)
        this.changeOverviewInfo(levelInfo.levelName, levelInfo.levelLength, levelInfo.levelObjectsCount)

        return true
    }

    loadLevelOnOtherSide = (levelName) => {

        $('p.objects-count').html(`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`);
        $('p.level-length').html(`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`);

        $('p.objects-count').addClass('gradient');
        $('p.level-length').addClass('gradient');

        return new Promise((resolve, reject) => {
            eel.load_database()().then(() => {
                eel.load_level_by_name(levelName)().then(() => {
                    resolve(true)
                })
            })
        })
    }

    openFileDialog = () => { return new Promise((resolve, reject) => {
            eel.call_open_file_dialog("Choose part...", [["GD Level (*.gmd)", "gmd"], ["All files", "*.*"]])().then((e) => {
                resolve(e)
            })
        }) 
    }

    importPartGmd = () => {
        return new Promise((resolveImport, reject) => {
            this.openFileDialog().then((path) => {
                if (path == null)
                    reject("No part selected.")
                else
                    eel.load_part_by_path(path)().then((gmd) => {
                        resolveImport(gmd)
                    })
            })
        })
    }

    renderMergeOffcanvasSwitch = (id, title, description) => {
        return `<div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" role="switch" id="${id}">
                    <label class="form-check-label" for="flexSwitchCheckDisabled">${title}<br>
                        <em><sub>${description}</sub></em>
                    </label>
                </div><br><br>`
    }

    addMergeOffcanvasSwitch = (id, title, description) => {
        const switchHtml = this.renderMergeOffcanvasSwitch(id, title, description)
        $('.offcanvas-body-checkboxes').append(switchHtml)
    }

    activateMergeOffcanvas = () => {
        const offcanvasElementList = [].slice.call(document.querySelectorAll('.offcanvas'))
        const offcanvasList = offcanvasElementList.map(function (offcanvasEl) {
            return new bootstrap.Offcanvas(offcanvasEl)
        })

        offcanvasList[0].show()
    }

    deactivateMergeOffcanvas = () => {
        //$('.offcanvas').hide()
    }

    processMergeOffcanvas = () => {

        $('.offcanvas-body-checkboxes').html("")

        this.addMergeOffcanvasSwitch('put-different-layers', 'Put part on different layer', 'Next free editor layer')
        this.addMergeOffcanvasSwitch('convert-colors', 'Convert colors to color triggers', 'Convert all used colors to color triggers')

        this.activateMergeOffcanvas()
    }

    putAndMergePart = () => {
        const part_index = $('select')[0].selectedIndex
        const put_different_layers = $('#put-different-layers')[0].checked
        const convert_colors = $('#convert-colors')[0].checked

        eel.put_and_merge_part(part_index, put_different_layers, convert_colors)()
    }

    bindButtons = () => {
        $('.reload-level-btn').click(() => {
            Swal.fire({
                title: 'Are you sure?',
                text: "You will lose all changes!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes!'
            }).then((result) => {
                if (result.isConfirmed) {
                        this.onEditorStateChange({
                            is_in_editor: true,
                            editor_level_name: this.workspaceName
                        })
                    }
              })
        })

        $('.import-part-gmd').click(() => {
            this.importPartGmd().then((gmd) => {
                $('.parts-list').append(`<option value="${gmd.k2}" class="part-option">${gmd.k2}</option>`)
            })
        })

        $('.merge-part-btn').click(() => {
            this.processMergeOffcanvas()
        })

        $('.put-n-merge').click(() => {
            this.putAndMergePart()
        })
    }

    constructor() {
        this.bindButtons()
    }
}

$(document).ready(() => {
    let app = new App()
    globalThis._app = app

    eel.expose(app.onLevelLoad, 'on_level_load')
    eel.expose(app.onEditorStateChange, 'on_editor_trigger_callback')
    eel.start_editor_checking_loop()()
})

