"""
Implements a network visualization in PyTorch.
Make sure to write device-agnostic code. For any function, initialize new tensors
on the same device as input tensors
"""

import torch


def hello():
    """
    This is a sample function that we will try to import and run to ensure that
    our environment is correctly set up on Google Colab.
    """
    print("Hello from network_visualization.py!")


def compute_saliency_maps(X, y, model):
    """
    Compute a class saliency map using the model for images X and labels y.

    Input:
    - X: Input images; Tensor of shape (N, 3, H, W)
    - y: Labels for X; LongTensor of shape (N,)
    - model: A pretrained CNN that will be used to compute the saliency map.

    Returns:
    - saliency: A Tensor of shape (N, H, W) giving the saliency maps for the input
    images.
    """
    # Make input tensor require gradient
    X.requires_grad_()

    saliency = None
    ##############################################################################
    # TODO: Implement this function. Perform a forward and backward pass through #
    # the model to compute the gradient of the correct class score with respect  #
    # to each input image. You first want to compute the loss over the correct   #
    # scores (we'll combine losses across a batch by summing), and then compute  #
    # the gradients with a backward pass.                                        #
    # Hint: X.grad.data stores the gradients                                     #
    ##############################################################################
    # Replace "pass" statement with your code
    # Forward pass
    scores = model(X)  # Get the scores for each class
    
    # Select the correct class scores using the labels y
    correct_scores = scores.gather(1, y.view(-1, 1)).squeeze()  # Shape (N,)
    
    # Compute the loss (negative score, since we want gradients)
    loss = correct_scores.sum()

    # Backward pass to compute gradients with respect to X
    loss.backward()

    # Get the saliency map by taking the maximum absolute value over the 3 input channels
    saliency = X.grad.data.abs().max(dim=1)[0]  # Shape (N, H, W)

    ##############################################################################
    #               END OF YOUR CODE                                             #
    ##############################################################################
    return saliency


def make_adversarial_attack(X, target_y, model, max_iter=100, verbose=True):
    """
    Generate an adversarial attack that is close to X, but that the model classifies
    as target_y.

    Inputs:
    - X: Input image; Tensor of shape (1, 3, 224, 224)
    - target_y: An integer in the range [0, 1000)
    - model: A pretrained CNN
    - max_iter: Upper bound on number of iteration to perform
    - verbose: If True, it prints the pogress (you can use this flag for debugging)

    Returns:
    - X_adv: An image that is close to X, but that is classifed as target_y
    by the model.
    """
    # Initialize our adversarial attack to the input image, and make it require
    # gradient
    X_adv = X.clone()
    X_adv = X_adv.requires_grad_()

    learning_rate = 1
    ##############################################################################
    # TODO: Generate an adversarial attack X_adv that the model will classify    #
    # as the class target_y. You should perform gradient ascent on the score     #
    # of the target class, stopping when the model is fooled.                    #
    # When computing an update step, first normalize the gradient:               #
    #   dX = learning_rate * g / ||g||_2                                         #
    #                                                                            #
    # You should write a training loop.                                          #
    #                                                                            #
    # HINT: For most examples, you should be able to generate an adversarial     #
    # attack in fewer than 100 iterations of gradient ascent.                    #
    # You can print your progress over iterations to check your algorithm.       #
    ##############################################################################
    # Replace "pass" statement with your code
    for i in range(max_iter):
    # Zero the gradients
        if X_adv.grad is not None:
            X_adv.grad.data.zero_()
        
        # Forward pass
        scores = model(X_adv)

        # print(scores[0].shape)
        
        # Get the score for the target class
        target_score = scores[0, target_y]
        # print(target_score)
        
        
        # Compute the loss (target score to maximize it)
        loss = target_score
        
        # Backward pass to compute gradients
        loss.backward()
        
        # Normalize the gradients
        grad = X_adv.grad.data
        grad_norm = grad / grad.norm()

        # Update the image
        with torch.no_grad():
            X_adv += learning_rate * grad_norm

        # Check if the model classifies the image as the target class
        scores = model(X_adv)
        predicted_class = scores.argmax(dim=1).item()
        if verbose:
            print(f"Iteration {i + 1}: Predicted class = {predicted_class}, Target class = {target_y}")
        if predicted_class == target_y:
            break
    ##############################################################################
    #                             END OF YOUR CODE                               #
    ##############################################################################
    return X_adv


def class_visualization_step(img, target_y, model, **kwargs):
    """
    Performs gradient step update to generate an image that maximizes the
    score of target_y under a pretrained model.

    Inputs:
    - img: random image with jittering as a PyTorch tensor
    - target_y: Integer in the range [0, 1000) giving the index of the class
    - model: A pretrained CNN that will be used to generate the image

    Keyword arguments:
    - l2_reg: Strength of L2 regularization on the image
    - learning_rate: How big of a step to take
    """

    l2_reg = kwargs.pop("l2_reg", 1e-3)
    learning_rate = kwargs.pop("learning_rate", 25)
    ########################################################################
    # TODO: Use the model to compute the gradient of the score for the     #
    # class target_y with respect to the pixels of the image, and make a   #
    # gradient step on the image using the learning rate. Don't forget the #
    # L2 regularization term!                                              #
    # Be very careful about the signs of elements in your code.            #
    # Hint: You have to perform inplace operations on img.data to update   #
    # the generated image using gradient ascent & reset img.grad to zero   #
    # after each step.                                                     #
    ########################################################################
    # Replace "pass" statement with your code
    img.requires_grad_()

    # Zero the gradients from the previous step
    if img.grad is not None:
        img.grad.data.zero_()

    # Forward pass to compute scores
    scores = model(img)

    # Select the score for the target class
    target_score = scores[0, target_y]

    # Compute the loss with L2 regularization
    loss = target_score - l2_reg * img.norm()

    # Backward pass to compute gradients
    loss.backward()

    # Perform gradient ascent step (inplace operation)
    with torch.no_grad():
        img += learning_rate * img.grad / img.grad.norm()

    # Zero the gradients for the next step
    img.grad.data.zero_()
    ########################################################################
    #                             END OF YOUR CODE                         #
    ########################################################################
    return img
