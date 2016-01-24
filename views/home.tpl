% include('global/header.tpl', title='Enumerating your world...')
<div class="container">
    <div class="starter-template">
        <h1>Welcome to count.re</h1>
        <p class="lead">
            Sometimes we just need a counter, nothing magic, just a simple counter. <br />
            If you need this, then count.re is for you!
        </p>
        <p>&nbsp;</p>
        <div class="panel panel-primary">
            <div class="panel-heading">
                <h3 class="panel-title">Create a counter</h3>
            </div>
            <div class="panel-body">
                <form class="form-horizontal" method="POST" action="/count/create?method=web">
                    <fieldset>
                        <div class="form-group">
                            <label for="inputName" class="col-lg-1 control-label">Name</label>
                            <div class="col-lg-11">
                                <input type="text" name="counterName" class="form-control" id="inputName"
                                    placeholder="This will appear as the title of your counter.">
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="inputButtonText" class="col-lg-1 control-label">Button</label>
                            <div class="col-lg-11">
                                <input type="text" name="counterButton" class="form-control" id="inputButtonText"
                                    placeholder="Sometimes, submit is just boring. Maybe you want to pound it!">
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="col-lg-12">
                                <button type="submit" class="btn btn-primary">Create</button>
                            </div>
                        </div>
                    </fieldset>
                </form>
            </div>
        </div>
    </div>
</div>
% include('global/footer.tpl')