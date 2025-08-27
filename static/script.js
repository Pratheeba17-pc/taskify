async function toggleComplete(task_id) {
    const res= await fetch(`/completed/${task_id}`,
        {
            method:'POST'
        }
    );
    const data=await res.json();
    if(data.success){
        window.location.reload();
    }
}