% include('global/header.tpl', title=name)
<div class="container">
    <div class="starter-template">
        <div class="well well-lg">
            <h1>{{name}}</h1>
            <p id="counterVal" style="font-size: 42px;">
                {{value}}
            </p>
            <form class="form-horizontal" method="POST" action="?method=web">
                <fieldset>
                    <div class="form-group">
                        <div class="col-lg-12">
                            <button type="submit" class="btn btn-primary">{{buttonText}}</button>
                        </div>
                    </div>
                </fieldset>
            </form>
        </div>
        
        <div class="panel panel-primary">
            <div class="panel-heading">
                <h3 class="panel-title">Need to script it?</h3>
            </div>
            <div class="panel-body">
                <p>
                Increment your counter using curl:
                </p>
                <pre>curl -X POST https://count.re/{{id}}</pre>
            </div>
        </div>
    </div>
</div>
% include('global/footer.tpl')