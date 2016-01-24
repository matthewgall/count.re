% include('global/header.tpl', title=name)
<div class="container">
    <div class="starter-template">
        <div class="well well-lg">
            <h1>{{name}}</h1>
            <p style="font-size: 42px;">
                {{value}}
            </p>
        </div>
        <div class="panel panel-primary">
            <div class="panel-heading">
                <h3 class="panel-title">Increment by button</h3>
            </div>
            <div class="panel-body">
                <form class="form-horizontal">
                    <fieldset>
                        <div class="form-group">
                            <div class="col-lg-12">
                                <button type="submit" class="btn btn-primary">{{buttonText}}</button>
                            </div>
                        </div>
                    </fieldset>
                </form>
            </div>
        </div>
        
        <div class="panel panel-primary">
            <div class="panel-heading">
                <h3 class="panel-title">Increment by e-mail</h3>
            </div>
            <div class="panel-body">
                <p>
                    Lazy? Increment this counter by sending an e-mail using your client to 
                    <strong><a href="mailto:{{id}}@count.re">{{id}}@count.re</a></strong>
                </p>
            </div>
        </div>
        
        <div class="panel panel-primary">
            <div class="panel-heading">
                <h3 class="panel-title">Need to script it?</h3>
            </div>
            <div class="panel-body">
                <p>
                Increment your counter using curl:
                </p>
                <pre>curl -X POST https://count.re/count/{{id}}</pre>
                
                <p>
                Or use Python:
                </p>
                <pre style="text-align: left">
                import requests
                requests.post('https://count.re/count/{{id}}')</pre>
            </div>
        </div>
    </div>
</div>
% include('global/footer.tpl')