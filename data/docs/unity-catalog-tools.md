# Unity Catalog functions as agent tools

Unity Catalog (UC) is the governance layer of Databricks. Tables, models, volumes and
functions all live in a three-level namespace: catalog.schema.object.

## Functions as tools

A SQL or Python function registered in Unity Catalog can be exposed to an agent as a
tool. The function signature becomes the tool schema the model sees, and the
function body is what runs when the model calls it. Because the function is a UC
object, access control, audit logs and lineage apply automatically.

## Example

A function `main.sales.lookup_customer(customer_id STRING)` that returns a
customer's recent orders can be attached to a support agent. The model calls it with
a customer id, Databricks executes the SQL, and the rows come back as the tool
result. The agent never has direct access to the table, only to the function.

## Model Context Protocol

Databricks also exposes UC functions and other resources through managed MCP
(Model Context Protocol) servers, so agents built with any MCP-compatible framework
can discover and call them.
